#include <Windows.h>
#include <wingdi.h>
#include <iostream>

int main() {
	// Tiempo de espera
	Sleep(2500);
	
    // Obtener el contexto del dispositivo de la pantalla
    HDC hdcScreen = GetDC(NULL);

    // Obtener las dimensiones de la pantalla
    int screenWidth = GetSystemMetrics(SM_CXSCREEN);
    int screenHeight = GetSystemMetrics(SM_CYSCREEN);

    // Crear un contexto de dispositivo compatible
    HDC hdcMem = CreateCompatibleDC(hdcScreen);

    // Crear un objeto de mapa de bits compatible con el contexto de la pantalla
    HBITMAP hBitmap = CreateCompatibleBitmap(hdcScreen, screenWidth, screenHeight);

    // Seleccionar el nuevo objeto de mapa de bits en el contexto de dispositivo compatible
    SelectObject(hdcMem, hBitmap);

    // Copiar la pantalla al objeto de mapa de bits
    BitBlt(hdcMem, 0, 0, screenWidth, screenHeight, hdcScreen, 0, 0, SRCCOPY);

    // Guardar la imagen como un archivo BMP
    BITMAPINFOHEADER bi;
    bi.biSize = sizeof(BITMAPINFOHEADER);
    bi.biWidth = screenWidth;
    bi.biHeight = -screenHeight;  // Negativo para que la imagen sea orientada hacia arriba
    bi.biPlanes = 1;
    bi.biBitCount = 32;  // Puedes ajustar esto según tus necesidades
    bi.biCompression = BI_RGB;
    bi.biSizeImage = 0;
    bi.biXPelsPerMeter = 0;
    bi.biYPelsPerMeter = 0;
    bi.biClrUsed = 0;
    bi.biClrImportant = 0;

    // Nombre del archivo de salida
    const char* fileName = "captura_pantalla.bmp";

    // Crear y escribir el archivo BMP
    FILE* file = fopen(fileName, "wb");
    if (file != NULL) {
        BITMAPFILEHEADER bmfHeader;
        bmfHeader.bfType = 0x4D42;  // "BM"
        bmfHeader.bfSize = sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER) + screenWidth * screenHeight * 4;  // Tamaño del archivo
        bmfHeader.bfReserved1 = 0;
        bmfHeader.bfReserved2 = 0;
        bmfHeader.bfOffBits = sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER);

        // Escribir encabezado del archivo
        fwrite(&bmfHeader, 1, sizeof(BITMAPFILEHEADER), file);

        // Escribir encabezado de la información de la imagen
        fwrite(&bi, 1, sizeof(BITMAPINFOHEADER), file);

        // Escribir datos de la imagen
        DWORD dwBmpSize = ((screenWidth * bi.biBitCount + 31) / 32) * 4 * screenHeight;
        BYTE* bmpBuffer = new BYTE[dwBmpSize];
        GetBitmapBits(hBitmap, dwBmpSize, bmpBuffer);
        fwrite(bmpBuffer, 1, dwBmpSize, file);

        // Cerrar el archivo
        fclose(file);

        // Limpiar la memoria
        delete[] bmpBuffer;
    }

    // Liberar recursos
    DeleteObject(hBitmap);
    DeleteDC(hdcMem);
    ReleaseDC(NULL, hdcScreen);

    return 0;
}
