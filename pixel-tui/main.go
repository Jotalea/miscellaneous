package main

import (
	"errors"
	"fmt"
	"io"
	"os"
	"strconv"
	"strings"

	"golang.org/x/term"
)

const (
	ansiReset       = "\x1b[0m"
	ansiClear       = "\x1b[2J"
	ansiHome        = "\x1b[H"
	ansiHideCursor  = "\x1b[?25l"
	ansiShowCursor  = "\x1b[?25h"
	ansiMouseEnable = "\x1b[?1000h\x1b[?1002h\x1b[?1006h"
	ansiMouseOff    = "\x1b[?1000l\x1b[?1002l\x1b[?1006l"

	sidebarWidth      = 27
	maxHistory        = 100
	exportANSIPath    = "piskel-term.ansi"
	exportUnicodePath = "piskel-term.unicode"
)

type RGB struct {
	R uint8
	G uint8
	B uint8
}

type Pixel struct {
	RGB
	On bool
}

// Cell is the persistent drawing unit. Each terminal cell retains top and bottom
// pixels so --half-blocks can render both halves. In the default full-block mode,
// normal drawing treats the entire cell as one solid pixel.
type Cell struct {
	Top    Pixel
	Bottom Pixel
}

type Point struct {
	X int
	Y int
}

type Rect struct {
	X0 int
	Y0 int
	X1 int
	Y1 int
}

type Clip struct {
	W     int
	H     int
	Cells []Cell
}

type Tool int

const (
	ToolPencil Tool = iota
	ToolBucket
	ToolLine
	ToolRectangle
	ToolSelect
	ToolMove
)

func (t Tool) String() string {
	switch t {
	case ToolPencil:
		return "Pencil"
	case ToolBucket:
		return "Bucket"
	case ToolLine:
		return "Line"
	case ToolRectangle:
		return "Rectangle"
	case ToolSelect:
		return "Select"
	case ToolMove:
		return "Move"
	default:
		return "Unknown"
	}
}

var palette = []RGB{
	{R: 255, G: 255, B: 255},
	{R: 0, G: 0, B: 0},
	{R: 255, G: 0, B: 0},
	{R: 255, G: 128, B: 0},
	{R: 255, G: 220, B: 0},
	{R: 0, G: 200, B: 80},
	{R: 0, G: 170, B: 255},
	{R: 80, G: 90, B: 255},
	{R: 180, G: 70, B: 220},
	{R: 255, G: 80, B: 170},
	{R: 130, G: 130, B: 140},
	{R: 70, G: 70, B: 80},
}

var terminalBackground = RGB{R: 20, G: 22, B: 28}

// Canvas double-buffers persistent terminal cells. The front buffer is the
// committed artwork and the back buffer is used during an edit transaction.
type Canvas struct {
	W     int
	H     int
	front []Cell
	back  []Cell
}

func NewCanvas(w, h int) *Canvas {
	if w < 1 {
		w = 1
	}
	if h < 1 {
		h = 1
	}
	return &Canvas{
		W:     w,
		H:     h,
		front: make([]Cell, w*h),
		back:  make([]Cell, w*h),
	}
}

func (c *Canvas) Snapshot() []Cell {
	copyOf := make([]Cell, len(c.front))
	copy(copyOf, c.front)
	return copyOf
}

func (c *Canvas) Apply(fn func([]Cell)) {
	copy(c.back, c.front)
	fn(c.back)
	c.front, c.back = c.back, c.front
}

func (c *Canvas) Restore(snapshot []Cell) {
	if len(snapshot) != len(c.front) {
		return
	}
	copy(c.back, snapshot)
	c.front, c.back = c.back, c.front
}

func sameRGB(a, b RGB) bool {
	return a.R == b.R && a.G == b.G && a.B == b.B
}

func samePixel(a, b Pixel) bool {
	return a.On == b.On && sameRGB(a.RGB, b.RGB)
}

func sameCell(a, b Cell) bool {
	return samePixel(a.Top, b.Top) && samePixel(a.Bottom, b.Bottom)
}

func sameCells(a, b []Cell) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if !sameCell(a[i], b[i]) {
			return false
		}
	}
	return true
}

func cloneCells(src []Cell) []Cell {
	dst := make([]Cell, len(src))
	copy(dst, src)
	return dst
}

func clonePixels(src []Pixel) []Pixel {
	dst := make([]Pixel, len(src))
	copy(dst, src)
	return dst
}

func coloredCell(color RGB) Cell {
	pixel := Pixel{RGB: color, On: true}
	return Cell{Top: pixel, Bottom: pixel}
}

func normalizeRect(a, b Point) Rect {
	r := Rect{X0: a.X, Y0: a.Y, X1: b.X, Y1: b.Y}
	if r.X0 > r.X1 {
		r.X0, r.X1 = r.X1, r.X0
	}
	if r.Y0 > r.Y1 {
		r.Y0, r.Y1 = r.Y1, r.Y0
	}
	return r
}

func (r Rect) Width() int {
	return r.X1 - r.X0 + 1
}

func (r Rect) Height() int {
	return r.Y1 - r.Y0 + 1
}

func (r Rect) Valid() bool {
	return r.X0 <= r.X1 && r.Y0 <= r.Y1
}

func (r Rect) Contains(x, y int) bool {
	return r.Valid() && x >= r.X0 && x <= r.X1 && y >= r.Y0 && y <= r.Y1
}

func intersectRect(r Rect, w, h int) (Rect, bool) {
	if r.X0 < 0 {
		r.X0 = 0
	}
	if r.Y0 < 0 {
		r.Y0 = 0
	}
	if r.X1 >= w {
		r.X1 = w - 1
	}
	if r.Y1 >= h {
		r.Y1 = h - 1
	}
	return r, r.Valid() && r.X0 < w && r.Y0 < h
}

func setCell(cells []Cell, w, h, x, y int, value Cell) {
	if x < 0 || y < 0 || x >= w || y >= h {
		return
	}
	cells[y*w+x] = value
}

func setCellHalf(cells []Cell, w, h, x, y, half int, value Pixel) {
	if x < 0 || y < 0 || x >= w || y >= h {
		return
	}
	if half == 0 {
		cells[y*w+x].Top = value
	} else {
		cells[y*w+x].Bottom = value
	}
}

func drawLineHalf(cells []Cell, w, h int, a, b Point, half int, value Pixel) {
	x0, y0 := a.X, a.Y
	x1, y1 := b.X, b.Y
	dx := abs(x1 - x0)
	sx := -1
	if x0 < x1 {
		sx = 1
	}
	dy := -abs(y1 - y0)
	sy := -1
	if y0 < y1 {
		sy = 1
	}
	err := dx + dy
	for {
		setCellHalf(cells, w, h, x0, y0, half, value)
		if x0 == x1 && y0 == y1 {
			return
		}
		e2 := 2 * err
		if e2 >= dy {
			err += dy
			x0 += sx
		}
		if e2 <= dx {
			err += dx
			y0 += sy
		}
	}
}

func drawLineCells(cells []Cell, w, h int, a, b Point, value Cell) {
	x0, y0 := a.X, a.Y
	x1, y1 := b.X, b.Y
	dx := abs(x1 - x0)
	sx := -1
	if x0 < x1 {
		sx = 1
	}
	dy := -abs(y1 - y0)
	sy := -1
	if y0 < y1 {
		sy = 1
	}
	err := dx + dy
	for {
		setCell(cells, w, h, x0, y0, value)
		if x0 == x1 && y0 == y1 {
			return
		}
		e2 := 2 * err
		if e2 >= dy {
			err += dy
			x0 += sx
		}
		if e2 <= dx {
			err += dx
			y0 += sy
		}
	}
}

func drawRectangleCells(cells []Cell, w, h int, r Rect, value Cell) {
	if !r.Valid() {
		return
	}
	for x := r.X0; x <= r.X1; x++ {
		setCell(cells, w, h, x, r.Y0, value)
		setCell(cells, w, h, x, r.Y1, value)
	}
	for y := r.Y0; y <= r.Y1; y++ {
		setCell(cells, w, h, r.X0, y, value)
		setCell(cells, w, h, r.X1, y, value)
	}
}

func floodFillCells(cells []Cell, w, h int, start Point, replacement Cell) {
	if start.X < 0 || start.Y < 0 || start.X >= w || start.Y >= h {
		return
	}
	startIndex := start.Y*w + start.X
	target := cells[startIndex]
	if sameCell(target, replacement) {
		return
	}
	queue := make([]Point, 1, w*h)
	queue[0] = start
	cells[startIndex] = replacement
	for head := 0; head < len(queue); head++ {
		p := queue[head]
		neighbors := [...]Point{{X: p.X - 1, Y: p.Y}, {X: p.X + 1, Y: p.Y}, {X: p.X, Y: p.Y - 1}, {X: p.X, Y: p.Y + 1}}
		for _, n := range neighbors {
			if n.X < 0 || n.Y < 0 || n.X >= w || n.Y >= h {
				continue
			}
			idx := n.Y*w + n.X
			if sameCell(cells[idx], target) {
				cells[idx] = replacement
				queue = append(queue, n)
			}
		}
	}
}

func clearRectCells(cells []Cell, w, h int, r Rect) {
	r, ok := intersectRect(r, w, h)
	if !ok {
		return
	}
	for y := r.Y0; y <= r.Y1; y++ {
		for x := r.X0; x <= r.X1; x++ {
			cells[y*w+x] = Cell{}
		}
	}
}

// translateCells performs a cell-grid move using a source copy. Blank cells in
// the selected region are copied too, so cutout behavior is deterministic.
func translateCells(cells []Cell, w, h int, region Rect, dx, dy int) {
	region, ok := intersectRect(region, w, h)
	if !ok || (dx == 0 && dy == 0) {
		return
	}
	source := cloneCells(cells)
	clearRectCells(cells, w, h, region)
	for y := region.Y0; y <= region.Y1; y++ {
		for x := region.X0; x <= region.X1; x++ {
			dx2, dy2 := x+dx, y+dy
			if dx2 < 0 || dy2 < 0 || dx2 >= w || dy2 >= h {
				continue
			}
			cells[dy2*w+dx2] = source[y*w+x]
		}
	}
}

func stampClip(cells []Cell, w, h int, clip Clip, at Point) {
	for y := 0; y < clip.H; y++ {
		for x := 0; x < clip.W; x++ {
			dx, dy := at.X+x, at.Y+y
			if dx < 0 || dy < 0 || dx >= w || dy >= h {
				continue
			}
			cells[dy*w+dx] = clip.Cells[y*clip.W+x]
		}
	}
}

// canvasToSubpixels creates a transient 2:1 raster for previews only.
func canvasToSubpixels(cells []Cell, w, h int) []Pixel {
	pixels := make([]Pixel, w*h*2)
	for y := 0; y < h; y++ {
		for x := 0; x < w; x++ {
			cell := cells[y*w+x]
			pixels[(y*2)*w+x] = cell.Top
			pixels[(y*2+1)*w+x] = cell.Bottom
		}
	}
	return pixels
}

func previewCell(pixels []Pixel, w, x, y int) Cell {
	return Cell{Top: pixels[(y*2)*w+x], Bottom: pixels[(y*2+1)*w+x]}
}

func putSubpixel(pixels []Pixel, w, h, x, y int, value Pixel) {
	if x < 0 || y < 0 || x >= w || y >= h {
		return
	}
	pixels[y*w+x] = value
}

func drawLineSubpixels(pixels []Pixel, w, h int, a, b Point, value Pixel) {
	x0, y0 := a.X, a.Y
	x1, y1 := b.X, b.Y
	dx := abs(x1 - x0)
	sx := -1
	if x0 < x1 {
		sx = 1
	}
	dy := -abs(y1 - y0)
	sy := -1
	if y0 < y1 {
		sy = 1
	}
	err := dx + dy
	for {
		putSubpixel(pixels, w, h, x0, y0, value)
		if x0 == x1 && y0 == y1 {
			return
		}
		e2 := 2 * err
		if e2 >= dy {
			err += dy
			x0 += sx
		}
		if e2 <= dx {
			err += dx
			y0 += sy
		}
	}
}

func drawRectangleSubpixels(pixels []Pixel, w, h int, r Rect, value Pixel) {
	if !r.Valid() {
		return
	}
	for x := r.X0; x <= r.X1; x++ {
		putSubpixel(pixels, w, h, x, r.Y0, value)
		putSubpixel(pixels, w, h, x, r.Y1, value)
	}
	for y := r.Y0; y <= r.Y1; y++ {
		putSubpixel(pixels, w, h, r.X0, y, value)
		putSubpixel(pixels, w, h, r.X1, y, value)
	}
}

func clearRectSubpixels(pixels []Pixel, w, h int, r Rect) {
	r, ok := intersectRect(r, w, h)
	if !ok {
		return
	}
	for y := r.Y0; y <= r.Y1; y++ {
		for x := r.X0; x <= r.X1; x++ {
			pixels[y*w+x] = Pixel{}
		}
	}
}

func translateSubpixels(pixels []Pixel, w, h int, region Rect, dx, dy int) {
	region, ok := intersectRect(region, w, h)
	if !ok || (dx == 0 && dy == 0) {
		return
	}
	source := clonePixels(pixels)
	clearRectSubpixels(pixels, w, h, region)
	for y := region.Y0; y <= region.Y1; y++ {
		for x := region.X0; x <= region.X1; x++ {
			dx2, dy2 := x+dx, y+dy
			if dx2 < 0 || dy2 < 0 || dx2 >= w || dy2 >= h {
				continue
			}
			pixels[dy2*w+dx2] = source[y*w+x]
		}
	}
}

func abs(n int) int {
	if n < 0 {
		return -n
	}
	return n
}

type eventKind int

const (
	eventKey eventKind = iota
	eventMouse
)

type InputEvent struct {
	Kind    eventKind
	Key     byte
	Special byte
	Mouse   MouseEvent
}

type MouseEvent struct {
	Button int
	X      int
	Y      int
	Press  bool
	Motion bool
	Mods   int
}

func readByte(r io.Reader) (byte, error) {
	var one [1]byte
	for {
		n, err := r.Read(one[:])
		if n > 0 {
			return one[0], nil
		}
		if err != nil {
			return 0, err
		}
	}
}

func readInput(r io.Reader) (InputEvent, error) {
	first, err := readByte(r)
	if err != nil {
		return InputEvent{}, err
	}
	if first != 0x1b {
		return InputEvent{Kind: eventKey, Key: first}, nil
	}

	second, err := readByte(r)
	if err != nil {
		return InputEvent{Kind: eventKey, Key: 0x1b}, nil
	}
	if second != '[' && second != 'O' {
		return InputEvent{Kind: eventKey, Key: 0x1b}, nil
	}

	third, err := readByte(r)
	if err != nil {
		return InputEvent{Kind: eventKey, Key: 0x1b}, nil
	}
	if second == '[' && third == '<' {
		var sequence strings.Builder
		for sequence.Len() < 64 {
			b, readErr := readByte(r)
			if readErr != nil {
				return InputEvent{}, readErr
			}
			if b == 'M' || b == 'm' {
				parts := strings.Split(sequence.String(), ";")
				if len(parts) != 3 {
					return InputEvent{}, errors.New("malformed SGR mouse event")
				}
				buttonCode, e1 := strconv.Atoi(parts[0])
				x, e2 := strconv.Atoi(parts[1])
				y, e3 := strconv.Atoi(parts[2])
				if e1 != nil || e2 != nil || e3 != nil {
					return InputEvent{}, errors.New("invalid SGR mouse coordinates")
				}
				return InputEvent{Kind: eventMouse, Mouse: MouseEvent{
					Button: buttonCode & 3,
					X:      x,
					Y:      y,
					Press:  b == 'M',
					Motion: buttonCode&32 != 0,
					Mods:   (buttonCode >> 2) & 7,
				}}, nil
			}
			sequence.WriteByte(b)
		}
		return InputEvent{}, errors.New("oversized SGR mouse event")
	}

	if second == 'O' {
		return InputEvent{Kind: eventKey, Special: third}, nil
	}
	if third >= 'A' && third <= 'Z' {
		return InputEvent{Kind: eventKey, Special: third}, nil
	}
	if third >= 'a' && third <= 'z' {
		return InputEvent{Kind: eventKey, Special: third}, nil
	}

	for i := 0; i < 32; i++ {
		b, readErr := readByte(r)
		if readErr != nil {
			return InputEvent{}, readErr
		}
		if b >= 0x40 && b <= 0x7e {
			return InputEvent{Kind: eventKey, Special: b}, nil
		}
	}
	return InputEvent{}, errors.New("oversized CSI keyboard event")
}

type App struct {
	canvas     *Canvas
	halfBlocks bool
	tool       Tool
	color      RGB
	palIdx     int

	cursorX     int
	cursorY     int
	previewHalf int

	selection    Rect
	hasSelection bool
	clipboard    *Clip

	undo [][]Cell
	redo [][]Cell

	dragging      bool
	dragButton    int
	dragStart     Point
	dragCurrent   Point
	dragStartHalf int
	dragHalf      int
	lastPoint     Point
	gestureBefore []Cell
	previewPixels []Pixel
	status        string
	quit          bool
}

func NewApp(w, h int, halfBlocks bool) *App {
	return &App{
		canvas:      NewCanvas(w, h),
		halfBlocks:  halfBlocks,
		tool:        ToolPencil,
		color:       palette[0],
		palIdx:      0,
		previewHalf: 0,
		cursorX:     w / 2,
		cursorY:     h / 2,
		status:      "Ready. Draw with the left mouse button.",
	}
}

func (a *App) activeCell(erasing bool) Cell {
	if erasing {
		return Cell{}
	}
	return coloredCell(a.color)
}

func (a *App) previewPixel() Pixel {
	return Pixel{RGB: a.color, On: true}
}

func (a *App) record(before []Cell) {
	after := a.canvas.Snapshot()
	if sameCells(before, after) {
		return
	}
	a.undo = append(a.undo, before)
	if len(a.undo) > maxHistory {
		a.undo = a.undo[len(a.undo)-maxHistory:]
	}
	a.redo = nil
}

func (a *App) applyEdit(fn func([]Cell)) {
	before := a.canvas.Snapshot()
	a.canvas.Apply(fn)
	a.record(before)
}

func (a *App) beginGesture() {
	a.gestureBefore = a.canvas.Snapshot()
}

func (a *App) commitGesture() {
	if a.gestureBefore != nil {
		a.record(a.gestureBefore)
	}
	a.gestureBefore = nil
}

func (a *App) cancelPreview() {
	a.previewPixels = nil
	a.dragging = false
	a.gestureBefore = nil
	a.dragButton = 0
}

func (a *App) undoEdit() {
	a.cancelPreview()
	if len(a.undo) == 0 {
		a.status = "Nothing to undo."
		return
	}
	current := a.canvas.Snapshot()
	last := a.undo[len(a.undo)-1]
	a.undo = a.undo[:len(a.undo)-1]
	a.redo = append(a.redo, current)
	a.canvas.Restore(last)
	a.status = "Undo."
}

func (a *App) redoEdit() {
	a.cancelPreview()
	if len(a.redo) == 0 {
		a.status = "Nothing to redo."
		return
	}
	current := a.canvas.Snapshot()
	last := a.redo[len(a.redo)-1]
	a.redo = a.redo[:len(a.redo)-1]
	a.undo = append(a.undo, current)
	a.canvas.Restore(last)
	a.status = "Redo."
}

func (a *App) copySelection() {
	if !a.hasSelection {
		a.status = "Copy needs an active rectangular selection."
		return
	}
	r, ok := intersectRect(a.selection, a.canvas.W, a.canvas.H)
	if !ok {
		a.status = "Selection is outside the canvas."
		return
	}
	clip := Clip{W: r.Width(), H: r.Height(), Cells: make([]Cell, r.Width()*r.Height())}
	for y := 0; y < clip.H; y++ {
		copy(clip.Cells[y*clip.W:(y+1)*clip.W], a.canvas.front[(r.Y0+y)*a.canvas.W+r.X0:(r.Y0+y)*a.canvas.W+r.X1+1])
	}
	a.clipboard = &clip
	a.status = fmt.Sprintf("Copied %d x %d cells.", clip.W, clip.H)
}

func (a *App) cutSelection() {
	if !a.hasSelection {
		a.status = "Cut needs an active rectangular selection."
		return
	}
	a.copySelection()
	if a.clipboard == nil {
		return
	}
	r := a.selection
	a.applyEdit(func(cells []Cell) { clearRectCells(cells, a.canvas.W, a.canvas.H, r) })
	a.status = fmt.Sprintf("Cut %d x %d cells.", a.clipboard.W, a.clipboard.H)
}

func (a *App) pasteClipboard() {
	if a.clipboard == nil {
		a.status = "Clipboard is empty. Select and copy first."
		return
	}
	clip := *a.clipboard
	at := Point{X: a.cursorX, Y: a.cursorY}
	a.applyEdit(func(cells []Cell) { stampClip(cells, a.canvas.W, a.canvas.H, clip, at) })
	a.status = fmt.Sprintf("Pasted %d x %d cells at %d,%d.", clip.W, clip.H, at.X, at.Y)
}

func (a *App) exportCurrent() {
	if err := a.exportTo(exportANSIPath, true); err != nil {
		a.status = "ANSI export failed: " + err.Error()
		return
	}
	if err := a.exportTo(exportUnicodePath, false); err != nil {
		a.status = "Unicode export failed: " + err.Error()
		return
	}
	a.status = "Exported piskel-term.ansi and piskel-term.unicode."
}

func (a *App) exportTo(path string, withANSI bool) error {
	var out strings.Builder
	if withANSI {
		out.WriteString(ansiReset)
	}
	for y := 0; y < a.canvas.H; y++ {
		for x := 0; x < a.canvas.W; x++ {
			cell := a.canvas.front[y*a.canvas.W+x]
			if withANSI {
				out.WriteString(ansiCellString(cell, a.halfBlocks))
			} else {
				out.WriteString(cellGlyph(cell, a.halfBlocks))
			}
		}
		if y+1 < a.canvas.H {
			out.WriteByte('\n')
		}
	}
	if withANSI {
		out.WriteString(ansiReset)
	}
	return os.WriteFile(path, []byte(out.String()), 0644)
}

func (a *App) moveCursor(dx, dy int) {
	a.cursorX += dx
	a.cursorY += dy
	if a.cursorX < 0 {
		a.cursorX = 0
	}
	if a.cursorY < 0 {
		a.cursorY = 0
	}
	if a.cursorX >= a.canvas.W {
		a.cursorX = a.canvas.W - 1
	}
	if a.cursorY >= a.canvas.H {
		a.cursorY = a.canvas.H - 1
	}
}

func (a *App) keyboardDraw() {
	point := Point{X: a.cursorX, Y: a.cursorY}
	switch a.tool {
	case ToolPencil:
		a.applyEdit(func(cells []Cell) { setCell(cells, a.canvas.W, a.canvas.H, point.X, point.Y, a.activeCell(false)) })
		a.status = fmt.Sprintf("Placed cell at %d,%d.", point.X, point.Y)
	case ToolBucket:
		a.applyEdit(func(cells []Cell) { floodFillCells(cells, a.canvas.W, a.canvas.H, point, a.activeCell(false)) })
		a.status = "Bucket filled."
	default:
		a.status = "Space draws with Pencil or Bucket; use the mouse for previews."
	}
}

func (a *App) setTool(t Tool) {
	a.cancelPreview()
	a.tool = t
	a.status = "Tool: " + t.String() + "."
}

func (a *App) choosePalette(index int) {
	if len(palette) == 0 {
		return
	}
	if index < 0 {
		index = len(palette) - 1
	}
	if index >= len(palette) {
		index = 0
	}
	a.palIdx = index
	a.color = palette[index]
	a.status = fmt.Sprintf("Color: #%02X%02X%02X.", a.color.R, a.color.G, a.color.B)
}

func (a *App) handleKey(ev InputEvent) {
	if ev.Special != 0 {
		switch ev.Special {
		case 'A':
			a.moveCursor(0, -1)
		case 'B':
			a.moveCursor(0, 1)
		case 'C':
			a.moveCursor(1, 0)
		case 'D':
			a.moveCursor(-1, 0)
		}
		return
	}

	switch ev.Key {
	case 0x11, 'q', 'Q':
		a.quit = true
	case 0x1b:
		a.cancelPreview()
		a.status = "Preview cancelled."
	case 0x1a:
		a.undoEdit()
	case 0x19:
		a.redoEdit()
	case 0x03:
		a.copySelection()
	case 0x18:
		a.cutSelection()
	case 0x16:
		a.pasteClipboard()
	case 0x05, 0x13: // Ctrl-E or Ctrl-S.
		a.exportCurrent()
	case '\t':
		a.previewHalf ^= 1
		if a.previewHalf == 0 {
			a.status = "Preview guide: top half."
		} else {
			a.status = "Preview guide: bottom half."
		}
	case '[':
		a.choosePalette(a.palIdx - 1)
	case ']':
		a.choosePalette(a.palIdx + 1)
	case 'p', 'P':
		a.setTool(ToolPencil)
	case 'b', 'B':
		a.setTool(ToolBucket)
	case 'l', 'L':
		a.setTool(ToolLine)
	case 'r', 'R':
		a.setTool(ToolRectangle)
	case 's', 'S':
		a.setTool(ToolSelect)
	case 'm', 'M':
		a.setTool(ToolMove)
	case ' ', '\n', '\r':
		a.keyboardDraw()
	case 0x0e: // Ctrl-N: clear the canvas as one undoable edit.
		a.applyEdit(func(cells []Cell) {
			for i := range cells {
				cells[i] = Cell{}
			}
		})
		a.status = "Canvas cleared."
	}
}

func (a *App) screenToCell(screenX, screenY int) (Point, bool) {
	canvasX := sidebarWidth + 2
	canvasY := 2
	cellX := screenX - canvasX
	cellY := screenY - canvasY
	if cellX < 0 || cellY < 0 || cellX >= a.canvas.W || cellY >= a.canvas.H {
		return Point{}, false
	}
	return Point{X: cellX, Y: cellY}, true
}

func (a *App) subPoint(point Point, half int) Point {
	if half < 0 {
		half = 0
	}
	if half > 1 {
		half = 1
	}
	return Point{X: point.X, Y: point.Y*2 + half}
}

func (a *App) buildPreview() {
	if !a.dragging {
		return
	}
	base := canvasToSubpixels(a.canvas.Snapshot(), a.canvas.W, a.canvas.H)
	previewHeight := a.canvas.H * 2
	value := a.previewPixel()
	switch a.tool {
	case ToolLine:
		drawLineSubpixels(base, a.canvas.W, previewHeight, a.subPoint(a.dragStart, a.dragStartHalf), a.subPoint(a.dragCurrent, a.dragHalf), value)
		a.previewPixels = base
	case ToolRectangle:
		start := a.subPoint(a.dragStart, a.dragStartHalf)
		end := a.subPoint(a.dragCurrent, a.dragHalf)
		drawRectangleSubpixels(base, a.canvas.W, previewHeight, normalizeRect(start, end), value)
		a.previewPixels = base
	case ToolMove:
		region := Rect{X0: 0, Y0: 0, X1: a.canvas.W - 1, Y1: previewHeight - 1}
		if a.hasSelection {
			region = Rect{X0: a.selection.X0, Y0: a.selection.Y0 * 2, X1: a.selection.X1, Y1: a.selection.Y1*2 + 1}
		}
		translateSubpixels(base, a.canvas.W, previewHeight, region, a.dragCurrent.X-a.dragStart.X, (a.dragCurrent.Y-a.dragStart.Y)*2)
		a.previewPixels = base
	}
}

func (a *App) startMouseGesture(button int, point Point, half int) {
	a.dragging = true
	a.dragButton = button
	a.dragStart = point
	a.dragCurrent = point
	a.dragStartHalf = half
	a.dragHalf = half
	a.lastPoint = point
	a.previewPixels = nil
	if button == 2 {
		a.beginGesture()
		if a.halfBlocks {
			value := Pixel{}
			a.canvas.Apply(func(cells []Cell) { setCellHalf(cells, a.canvas.W, a.canvas.H, point.X, point.Y, half, value) })
		} else {
			a.canvas.Apply(func(cells []Cell) { setCell(cells, a.canvas.W, a.canvas.H, point.X, point.Y, Cell{}) })
		}
		return
	}
	switch a.tool {
	case ToolPencil:
		a.beginGesture()
		if a.halfBlocks {
			value := a.previewPixel()
			a.canvas.Apply(func(cells []Cell) { setCellHalf(cells, a.canvas.W, a.canvas.H, point.X, point.Y, half, value) })
		} else {
			a.canvas.Apply(func(cells []Cell) { setCell(cells, a.canvas.W, a.canvas.H, point.X, point.Y, a.activeCell(false)) })
		}
	case ToolBucket:
		a.applyEdit(func(cells []Cell) { floodFillCells(cells, a.canvas.W, a.canvas.H, point, a.activeCell(false)) })
		a.dragging = false
		a.status = "Bucket filled."
	case ToolSelect, ToolLine, ToolRectangle, ToolMove:
		a.buildPreview()
	}
}

func (a *App) updateMouseGesture(point Point, half int) {
	if !a.dragging {
		return
	}
	a.cursorX, a.cursorY = point.X, point.Y
	a.dragCurrent = point
	a.dragHalf = half
	if a.dragButton == 2 || a.tool == ToolPencil {
		if a.halfBlocks {
			value := Pixel{}
			if a.dragButton != 2 {
				value = a.previewPixel()
			}
			a.canvas.Apply(func(cells []Cell) { drawLineHalf(cells, a.canvas.W, a.canvas.H, a.lastPoint, point, half, value) })
		} else if a.dragButton == 2 {
			a.canvas.Apply(func(cells []Cell) { drawLineCells(cells, a.canvas.W, a.canvas.H, a.lastPoint, point, Cell{}) })
		} else {
			a.canvas.Apply(func(cells []Cell) {
				drawLineCells(cells, a.canvas.W, a.canvas.H, a.lastPoint, point, a.activeCell(false))
			})
		}
		a.lastPoint = point
		return
	}
	a.buildPreview()
}

func (a *App) finishMouseGesture() {
	if !a.dragging {
		return
	}
	switch {
	case a.dragButton == 2 || a.tool == ToolPencil:
		a.commitGesture()
	case a.tool == ToolLine:
		start, end := a.dragStart, a.dragCurrent
		a.applyEdit(func(cells []Cell) { drawLineCells(cells, a.canvas.W, a.canvas.H, start, end, a.activeCell(false)) })
	case a.tool == ToolRectangle:
		r := normalizeRect(a.dragStart, a.dragCurrent)
		a.applyEdit(func(cells []Cell) { drawRectangleCells(cells, a.canvas.W, a.canvas.H, r, a.activeCell(false)) })
	case a.tool == ToolSelect:
		a.selection = normalizeRect(a.dragStart, a.dragCurrent)
		a.hasSelection = true
		a.status = fmt.Sprintf("Selected %d x %d cells.", a.selection.Width(), a.selection.Height())
	case a.tool == ToolMove:
		dx := a.dragCurrent.X - a.dragStart.X
		dy := a.dragCurrent.Y - a.dragStart.Y
		region := Rect{X0: 0, Y0: 0, X1: a.canvas.W - 1, Y1: a.canvas.H - 1}
		if a.hasSelection {
			region = a.selection
		}
		a.applyEdit(func(cells []Cell) { translateCells(cells, a.canvas.W, a.canvas.H, region, dx, dy) })
		if a.hasSelection {
			a.selection = Rect{X0: a.selection.X0 + dx, Y0: a.selection.Y0 + dy, X1: a.selection.X1 + dx, Y1: a.selection.Y1 + dy}
			if clipped, ok := intersectRect(a.selection, a.canvas.W, a.canvas.H); ok {
				a.selection = clipped
			} else {
				a.hasSelection = false
			}
		}
		a.status = fmt.Sprintf("Moved by %d,%d cells.", dx, dy)
	}
	a.previewPixels = nil
	a.dragging = false
	a.dragButton = 0
}

func (a *App) sidebarClick(x, y int) {
	toolRows := map[int]Tool{
		4: ToolPencil,
		5: ToolBucket,
		6: ToolLine,
		7: ToolRectangle,
		8: ToolSelect,
		9: ToolMove,
	}
	if t, ok := toolRows[y]; ok {
		a.setTool(t)
		return
	}
	if y == 12 {
		for i := range palette {
			left := 2 + i*2
			if x >= left && x < left+2 {
				a.choosePalette(i)
				return
			}
		}
	}
}

func (a *App) handleMouse(e MouseEvent) {
	screenX, screenY := e.X-1, e.Y-1

	// Always finish an active gesture on release, even if the pointer was
	// released outside the canvas or over the sidebar.
	if !e.Press && !e.Motion && a.dragging {
		if point, inside := a.screenToCell(screenX, screenY); inside {
			a.cursorX, a.cursorY = point.X, point.Y
			a.dragCurrent = point
			a.dragHalf = a.previewHalf
		}
		a.finishMouseGesture()
		return
	}

	if screenX < sidebarWidth+2 {
		if e.Press && !e.Motion && e.Button == 0 {
			a.sidebarClick(screenX, screenY)
		}
		return
	}

	point, inside := a.screenToCell(screenX, screenY)
	if !inside {
		return
	}
	a.cursorX, a.cursorY = point.X, point.Y

	if e.Motion {
		a.updateMouseGesture(point, a.previewHalf)
		return
	}
	if e.Press {
		if e.Button == 0 {
			a.startMouseGesture(1, point, a.previewHalf)
		} else if e.Button == 2 {
			a.startMouseGesture(2, point, a.previewHalf)
		}
	}
}

func rgbEscape(prefix string, c RGB) string {
	return fmt.Sprintf("\x1b[%s;2;%d;%d;%dm", prefix, c.R, c.G, c.B)
}

func cellColors(cell Cell, halfBlocks bool) (fg, bg RGB, glyph string) {
	if !halfBlocks {
		// Full-block mode intentionally collapses both stored halves into one
		// terminal cell. The top color wins when both halves are populated.
		if cell.Top.On {
			return cell.Top.RGB, terminalBackground, "█"
		}
		if cell.Bottom.On {
			return cell.Bottom.RGB, terminalBackground, "█"
		}
		return terminalBackground, terminalBackground, " "
	}
	switch {
	case cell.Top.On && cell.Bottom.On && sameRGB(cell.Top.RGB, cell.Bottom.RGB):
		return cell.Top.RGB, terminalBackground, "█"
	case cell.Top.On && cell.Bottom.On:
		return cell.Top.RGB, cell.Bottom.RGB, "▀"
	case cell.Top.On:
		return cell.Top.RGB, terminalBackground, "▀"
	case cell.Bottom.On:
		return cell.Bottom.RGB, terminalBackground, "▄"
	default:
		return terminalBackground, terminalBackground, " "
	}
}

func cellGlyph(cell Cell, halfBlocks bool) string {
	_, _, glyph := cellColors(cell, halfBlocks)
	return glyph
}

func ansiCellString(cell Cell, halfBlocks bool) string {
	fg, bg, glyph := cellColors(cell, halfBlocks)
	return rgbEscape("38", fg) + rgbEscape("48", bg) + glyph + ansiReset
}

func cellString(cell Cell, cursor, selected, halfBlocks bool) string {
	fg, bg, glyph := cellColors(cell, halfBlocks)
	var b strings.Builder
	b.WriteString(rgbEscape("38", fg))
	b.WriteString(rgbEscape("48", bg))
	if selected || cursor {
		b.WriteString("\x1b[7m")
	}
	b.WriteString(glyph)
	if selected || cursor {
		b.WriteString("\x1b[27m")
	}
	b.WriteString(ansiReset)
	return b.String()
}

func clipASCII(s string, width int) string {
	if width <= 0 {
		return ""
	}
	if len(s) > width {
		return s[:width]
	}
	return s + strings.Repeat(" ", width-len(s))
}

func (a *App) selectionForDisplay() (Rect, bool) {
	if a.tool == ToolSelect && a.dragging {
		return normalizeRect(a.dragStart, a.dragCurrent), true
	}
	return a.selection, a.hasSelection
}

func (a *App) render() (string, error) {
	cols, rows, err := term.GetSize(int(os.Stdout.Fd()))
	if err != nil {
		return "", err
	}
	if cols < 1 || rows < 1 {
		return "", errors.New("terminal has invalid dimensions")
	}

	canvasX := sidebarWidth + 2
	canvasY := 2
	selection, hasSelection := a.selectionForDisplay()
	var out strings.Builder
	out.Grow(cols * rows * 12)
	out.WriteString(ansiHideCursor)
	out.WriteString(ansiHome)
	out.WriteString(ansiClear)

	writeAt := func(x, y int, text string) {
		if x < 0 || y < 0 || x >= cols || y >= rows {
			return
		}
		out.WriteString(fmt.Sprintf("\x1b[%d;%dH", y+1, x+1))
		out.WriteString(clipASCII(text, cols-x))
	}
	writeColoredAt := func(x, y int, text string, c RGB) {
		if x < 0 || y < 0 || x >= cols || y >= rows {
			return
		}
		out.WriteString(fmt.Sprintf("\x1b[%d;%dH", y+1, x+1))
		out.WriteString(rgbEscape("38", c))
		out.WriteString(clipASCII(text, cols-x))
		out.WriteString(ansiReset)
	}

	writeColoredAt(0, 0, " PISKEL-TERM ", RGB{R: 0, G: 220, B: 255})
	rendererName := "full-block"
	if a.halfBlocks {
		rendererName = "half-block"
	}
	writeAt(0, 1, "ANSI "+rendererName+" editor")
	writeColoredAt(0, 3, "TOOLS", RGB{R: 255, G: 190, B: 70})
	toolRows := []struct {
		row  int
		key  string
		tool Tool
	}{
		{4, "P", ToolPencil},
		{5, "B", ToolBucket},
		{6, "L", ToolLine},
		{7, "R", ToolRectangle},
		{8, "S", ToolSelect},
		{9, "M", ToolMove},
	}
	for _, item := range toolRows {
		marker := " "
		if a.tool == item.tool {
			marker = ">"
		}
		writeAt(0, item.row, fmt.Sprintf("%s [%s] %-12s", marker, item.key, item.tool.String()))
	}
	writeColoredAt(0, 11, "PALETTE", RGB{R: 255, G: 190, B: 70})
	for i, c := range palette {
		x := 2 + i*2
		if x+1 >= sidebarWidth || x >= cols || 12 >= rows {
			continue
		}
		out.WriteString(fmt.Sprintf("\x1b[13;%dH", x+1))
		out.WriteString(rgbEscape("48", c))
		if i == a.palIdx {
			out.WriteString("\x1b[7m")
		}
		out.WriteString("  ")
		out.WriteString(ansiReset)
	}
	writeAt(0, 14, fmt.Sprintf("Color #%02X%02X%02X", a.color.R, a.color.G, a.color.B))
	writeAt(0, 15, fmt.Sprintf("Canvas %dx%d cells", a.canvas.W, a.canvas.H))
	writeAt(0, 16, fmt.Sprintf("Cursor %d,%d", a.cursorX, a.cursorY))
	writeAt(0, 18, fmt.Sprintf("Mode: %s", rendererName))
	if hasSelection {
		writeAt(0, 17, fmt.Sprintf("Sel %d,%d-%d,%d", selection.X0, selection.Y0, selection.X1, selection.Y1))
	} else {
		writeAt(0, 17, "Sel none")
	}
	writeAt(0, 19, "Ctrl-Z/Y  undo/redo")
	writeAt(0, 20, "Ctrl-C/X/V  copy/cut/paste")
	writeAt(0, 21, "Ctrl-E/S  export ANSI+Unicode")
	writeAt(0, 22, "Arrows/Space  keyboard")
	writeAt(0, 23, "Q or Ctrl-Q  quit")
	writeColoredAt(0, rows-1, clipASCII(a.status, sidebarWidth), RGB{R: 180, G: 220, B: 180})

	cellAt := func(x, y int) Cell {
		if a.previewPixels != nil {
			return previewCell(a.previewPixels, a.canvas.W, x, y)
		}
		return a.canvas.front[y*a.canvas.W+x]
	}
	for y := 0; y < a.canvas.H; y++ {
		screenRow := canvasY + y
		if screenRow >= rows {
			break
		}
		if canvasX >= cols {
			break
		}
		out.WriteString(fmt.Sprintf("\x1b[%d;%dH", screenRow+1, canvasX+1))
		for x := 0; x < a.canvas.W && canvasX+x < cols; x++ {
			selected := false
			if hasSelection && (x == selection.X0 || x == selection.X1 || y == selection.Y0 || y == selection.Y1) && selection.Contains(x, y) {
				selected = true
			}
			cursor := x == a.cursorX && y == a.cursorY
			out.WriteString(cellString(cellAt(x, y), cursor, selected, a.halfBlocks))
		}
	}
	out.WriteString(fmt.Sprintf("\x1b[%d;%dH", rows, 1))
	out.WriteString(ansiReset)
	return out.String(), nil
}

func cleanup() {
	_, _ = os.Stdout.WriteString(ansiMouseOff + ansiShowCursor + ansiReset + "\x1b[H\x1b[2J")
}

func parseDimension(value string, fallback int) int {
	n, err := strconv.Atoi(value)
	if err != nil || n < 1 || n > 512 {
		return fallback
	}
	return n
}

func usage() string {
	return `piskel-term - terminal pixel editor

Usage:
  piskel-term [--half-blocks] [width height]

Options:
  --half-blocks  Opt in to half-block foreground/background rendering.
                  Full-block rendering is the default and is more stable.
  -h, --help      Show this help.

Examples:
  piskel-term
  piskel-term 64 32
  piskel-term --half-blocks 64 32
`
}

func parseArgs(args []string) (width, height int, halfBlocks, showHelp bool, err error) {
	width, height = 48, 24
	positionals := make([]string, 0, 2)
	for _, arg := range args {
		switch arg {
		case "--half-blocks":
			halfBlocks = true
		case "--full-blocks":
			halfBlocks = false
		case "-h", "--help":
			showHelp = true
		default:
			if strings.HasPrefix(arg, "-") {
				return 0, 0, false, false, fmt.Errorf("unknown option %q", arg)
			}
			if len(positionals) >= 2 {
				return 0, 0, false, false, errors.New("expected at most width and height")
			}
			positionals = append(positionals, arg)
		}
	}
	if len(positionals) > 0 {
		parsed, parseErr := strconv.Atoi(positionals[0])
		if parseErr != nil || parsed < 1 || parsed > 512 {
			return 0, 0, false, false, fmt.Errorf("invalid width %q: expected 1..512", positionals[0])
		}
		width = parsed
	}
	if len(positionals) > 1 {
		parsed, parseErr := strconv.Atoi(positionals[1])
		if parseErr != nil || parsed < 1 || parsed > 512 {
			return 0, 0, false, false, fmt.Errorf("invalid height %q: expected 1..512", positionals[1])
		}
		height = parsed
	}
	return width, height, halfBlocks, showHelp, nil
}

func main() {
	width, height, halfBlocks, showHelp, parseErr := parseArgs(os.Args[1:])
	if parseErr != nil {
		fmt.Fprintln(os.Stderr, parseErr)
		fmt.Fprintln(os.Stderr, usage())
		os.Exit(2)
	}
	if showHelp {
		fmt.Print(usage())
		return
	}

	if !term.IsTerminal(int(os.Stdin.Fd())) || !term.IsTerminal(int(os.Stdout.Fd())) {
		fmt.Fprintln(os.Stderr, "piskel-term must be run attached to an interactive terminal")
		os.Exit(1)
	}

	state, err := term.MakeRaw(int(os.Stdin.Fd()))
	if err != nil {
		fmt.Fprintf(os.Stderr, "enable raw terminal mode: %v\n", err)
		os.Exit(1)
	}
	defer func() {
		_ = term.Restore(int(os.Stdin.Fd()), state)
		cleanup()
	}()

	_, _ = os.Stdout.WriteString(ansiMouseEnable + ansiHideCursor + ansiClear + ansiHome)
	app := NewApp(width, height, halfBlocks)
	for !app.quit {
		frame, renderErr := app.render()
		if renderErr != nil {
			app.status = "Render error: " + renderErr.Error()
			break
		}
		if _, writeErr := os.Stdout.WriteString(frame); writeErr != nil {
			break
		}
		event, readErr := readInput(os.Stdin)
		if readErr != nil {
			break
		}
		if event.Kind == eventMouse {
			app.handleMouse(event.Mouse)
		} else {
			app.handleKey(event)
		}
	}
}
