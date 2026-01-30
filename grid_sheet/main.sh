#!/bin/bash

# Define the output file
OUTPUT="index.html"
TITLE=$(basename "$PWD")

cat <<EOF > $OUTPUT
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>$TITLE</title>
    <style>
        body { margin: 0; padding: 10mm; font-family: sans-serif; background: #f0f0f0; }
        .grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 5mm;
        }
        .photo-container {
            width: 100%;
            height: 135mm; /* Fits 2 rows perfectly on A4 */
            display: flex;
            align-items: center;
            justify-content: center;
            background: white;
            overflow: hidden;
        }
        img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }
        /* Page break logic for PDF export */
        @media print {
            body { padding: 0; background: white; }
            .photo-container:nth-child(4n) {
                page-break-after: always;
            }
            @page { size: A4; margin: 10mm; }
        }
    </style>
</head>
<body>
    <div class="grid">
EOF

# Loop through all jpg files and add them to the HTML
for file in *.jpg; do
    if [ -f "$file" ]; then
        echo "        <div class=\"photo-container\"><img src=\"$file\"></div>" >> $OUTPUT
    fi
done

cat <<EOF >> $OUTPUT
    </div>
</body>
</html>
EOF

echo "$OUTPUT has been generated with $(ls *.jpg | wc -l) images."
