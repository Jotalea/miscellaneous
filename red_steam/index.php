<?php

// NEED TO FIX POSTING MORE GAMES NOT WORKING BUT NOT SHOWING ANY ERRORS


// Definir la ruta del archivo JSON y leer su contenido
$jsonFilePath = 'games.json';
$jsonString = file_get_contents($jsonFilePath);
$data = json_decode($jsonString, true);

// Verificar si el formulario ha sido enviado
if (isset($_POST['enviar'])) {
    // Obtener los datos del formulario
    $nuevoNombre = trim($_POST['nombre']);
    $nuevoPlataforma = trim($_POST['plataforma']);
    $nuevoEnlace = trim($_POST['enlace']);

    // Validar el enlace
    $erroresEnlace = containsNoInvalidCharacters($nuevoEnlace) && containsValidWords($nuevoEnlace) && hasNoSpaces($nuevoEnlace) && isShortEnough($nuevoEnlace, 128) && seventhCharacterIsSlash($nuevoEnlace) && startsWithHttp($nuevoEnlace);

    // Validar el nombre
    $erroresNombre = containsNoInvalidCharacters($nuevoNombre) && isShortEnough($nuevoNombre, 64);

    // Si no hay errores, agregar el nuevo elemento al archivo JSON
    if (!$erroresEnlace && !$erroresNombre) {
        // Crear un nuevo array para el nuevo juego
        $nuevoJuego = array(
            "title" => $nuevoNombre,
            "platform" => $nuevoPlataforma,
            "links" => [
				array(
                    "primary" => true,
                    "link" => $nuevoEnlace
                )
            ]
        );

        // Agregar el nuevo juego al array principal
        array_push($data['games'], $nuevoJuego);

        // Codificar el array en JSON
        $newJsonString = json_encode($data, JSON_PRETTY_PRINT);

        // Actualizar el archivo JSON
        file_put_contents($jsonFilePath, $newJsonString);

        // Mostrar mensaje de confirmación
        echo '<p>Elemento agregado correctamente.</p>';
    } else {
        // Mostrar los errores
        echo '<div class="errores">';
        if ($erroresEnlace) {
                echo '<p>' . $error . '</p>';
        }
        if ($erroresNombre) {
                echo '<p>' . $error . '</p>';
        }
        echo '</div>';
    }
}

// Función para verificar si el enlace comienza con "http"
function startsWithHttp($enlace) {
    return substr($enlace, 0, 4) === "http";
}

// Función para verificar si el séptimo carácter del enlace es "/"
function seventhCharacterIsSlash($enlace) {
    return substr($enlace, 6, 1) === "/";
}

// Función para verificar si el enlace contiene palabras válidas
function containsValidWords($enlace) {
    $validWords = ["mediafire.com", "drive.google.com", "huggingface.co", "mega.nz"];
    foreach ($validWords as $word) {
        if (strpos($enlace, $word) !== false) {
            return true;
        }
    }
    return false;
}

// Función para verificar si el enlace no tiene espacios
function hasNoSpaces($enlace) {
    return strpos($enlace, ' ') === false;
}

// Función para verificar si el enlace no contiene caracteres inválidos
function containsNoInvalidCharacters($enlace) {
    $invalidCharacters = ["[", "]", "{", "}", "\"", "\\", "$", "%", "#"];
    foreach ($invalidCharacters as $char) {
        if (strpos($enlace, $char) !== false) {
            return false;
        }
    }
    return true;
}

// Función para verificar si la longitud del enlace es menor que el límite dado
function isShortEnough($enlace, $maxLength) {
    return strlen($enlace) < $maxLength;
}

?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="https://jotalea.com.ar/steam/icon.png">
    <title>Steam Rojo</title>
    <style>
		@import url("https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap");
        body {
            font-family: "Poppins", sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f8f8f8;
        }

        h1 {
            text-align: center;
            color: #333;
        }

        ul {
            list-style-type: none;
            padding: 0;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
        }

        li {
            background-color: #fff;
            padding: 15px;
            text-align: left;
            margin-right: 10px;
            margin-bottom: 10px;
            border-radius: 5px;
            width: 25%;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }

        .button-container {
            padding-top: 10px;
            text-align: left;
        }

		.form-container {
            max-width: 100%;
            margin: 20px auto;
            background-color: #cccccc;
            padding: 20px;
        }
        
        a.button {
            color: #fff;
            background-color: #007bff;
            padding: 8px 16px;
            border-radius: 5px;
            text-decoration: none;
            margin-right: 5px;
        }

        a.button:hover {
            background-color: #0056b3;
        }

        /* Media Query para ajustar el diseño en dispositivos móviles 
        @media (max-width: 600px) {
            li {
                padding: 10px;
            }
        }*/
    </style>
</head>
<body>
    <h1>Lista de Juegos de Jotalea</h1>
    <div class="centered">
        <ul id="gameList"></ul>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
        const jsonUrl = 'games.json?version=999';
        const gameList = document.getElementById('gameList');

        function loadGames() {
            fetch(jsonUrl)
                .then(response => response.json())
                .then(data => {
                    const games = data.games;
                    games.forEach(game => {
                        const title = game.title;
                        const platform = game.platform;
                        const links = game.links;

                        const listItem = document.createElement('li');
                        const gameInfo = `${title} (${platform})`;
                        listItem.textContent = gameInfo;

                        // Crear el contenedor para los botones de descarga
                        const buttonContainer = document.createElement('div');
                        buttonContainer.classList.add('button-container');

                        // Verificar si hay un enlace principal o partes
                        const primaryLink = links[0].primary;
                        const partsLinks = links[0].parts;

                        if (primaryLink) {
                            // Crear botón de descarga para el enlace principal
                            const downloadButton = createDownloadButton(primaryLink, 'Descargar');
                            buttonContainer.appendChild(downloadButton);
                        } else if (partsLinks) {
                            // Crear botones de descarga para cada parte del juego
                            partsLinks.forEach((partLink, index) => {
                                const buttonText = `Parte ${index + 1}`;
                                const downloadButton = createDownloadButton(partLink, buttonText);
                                buttonContainer.appendChild(downloadButton);
                            });
                        }

                        // Agregar el contenedor de botones al elemento <li>
                        listItem.appendChild(buttonContainer);

                        // Agregar el elemento <li> a la lista de juegos
                        gameList.appendChild(listItem);
                    });
                })
                .catch(error => {
                    console.error('Error al cargar el JSON:', error);
                });
            }
        
            function createDownloadButton(link, buttonText) {
                const downloadButton = document.createElement('a');
                downloadButton.setAttribute('href', link);
                downloadButton.setAttribute('target', '_blank');
                downloadButton.textContent = buttonText;
                downloadButton.classList.add('button');
                return downloadButton;
            }
        
            loadGames();
        });
    </script>

	<div class="container">
    <h1>Agregar juego a la lista (en mantenimiento)</h1>

    <form method="post">
        <label for="nombre">Juego:</label>
        <input type="text" id="nombre" name="nombre" required>

		<label for="plataforma">Plataforma:</label>
        <select name="plataforma" id="plataforma">
            <option value="Windows">Windows</option>
            <option value="Android">Android</option>
            <option value="Linux">Linux</option>
            
            <option value="PS1">PlayStation</option>
            <option value="PS2">PlayStation 2</option>
            <option value="PS3">PlayStation 3</option>
            <option value="PS4">PlayStation 4</option>
            <option value="PS5">PlayStation 5 (quien la tiene xdd)</option>
            <option value="PSP">PlayStation Portable</option>
            <option value="PSVita">PlayStation Vita</option>
            <option value="NES">Nintendo Entertainment System</option>
            <option value="SNES">Super Nintendo Entertainment System</option>
            <option value="N64">Nintendo 64</option>
            <option value="GameCube">Nintendo GameCube</option>
            <option value="Wii">Nintendo Wii</option>
            <option value="Wii U">Nintendo Wii U</option>
            <option value="Switch">Nintendo Switch</option>
            <option value="GB">Nintendo GameBoy</option>
            <option value="GBC">Nintendo GameBoy Color</option>
            <option value="GBA">Nintendo GameBoy Advance</option>
            <option value="DS">Nintendo DS</option>
            <option value="3DS">Nintendo 3DS</option>
            <option value="Xbox">Xbox</option>
            <option value="Xbox 360">Xbox 360</option>
            <option value="Xbox One">Xbox One</option>
            <option value="Xbox Series S">Xbox Series S</option>
            <option value="Xbox Series X">Xbox Series X</option>
            <option value="Otro">Otro dispositivo</option>
        </select>

        <label for="enlace">Link (se aceptan mediafire, drive, mega y huggingface):</label>
        <input type="text" id="enlace" name="enlace" required>

        <button type="submit" name="enviar">Enviar</button>
    </form>
    </div>
    
	<h2>Descargo de Responsabilidad</h2>
	<p>Bienvenido/a a nuestra página web de descargas de juegos gratuitos. Queremos informarte sobre algunos aspectos importantes antes de que utilices nuestro servicio:<br>- Contenido Publicado: Todos los juegos y enlaces de descarga disponibles en este sitio web son proporcionados por terceros y son ofrecidos de forma gratuita para propósitos de entretenimiento. No somos responsables del contenido publicado por estos terceros.<br>- Uso bajo tu Propia Responsabilidad: Al utilizar nuestro servicio y descargar juegos, aceptas que lo haces bajo tu propio riesgo y responsabilidad. No nos hacemos responsables de ningún daño, pérdida o consecuencia resultante del uso de cualquier juego o enlace de descarga disponible en este sitio.<br>- Verificación de Contenido: Recomendamos encarecidamente verificar la legalidad y seguridad de cada juego antes de descargarlo. Algunos juegos pueden estar sujetos a derechos de autor u otras restricciones legales.<br>- Limitación de Responsabilidad: En ningún caso seremos responsables por ningún tipo de daño directo, indirecto, incidental, especial, consecuencial o punitivo que surja del uso o la imposibilidad de utilizar nuestro servicio.<br>- Política de Derechos de Autor: Respetamos los derechos de autor y solicitamos a nuestros usuarios que hagan lo mismo. Si eres propietario de algún contenido y crees que se ha infringido tu derecho de autor, contáctanos de inmediato para resolver la situación.<br>Al utilizar este sitio web, aceptas y entiendes los términos de este descargo de responsabilidad. Te recomendamos leer nuestra política de privacidad y términos de uso para obtener más información sobre cómo utilizamos y protegemos tus datos personales.<br>Gracias por visitar nuestra página y disfrutar de nuestros servicios. Si tienes alguna pregunta o inquietud, no dudes en contactarnos.</p>

</body>
</html>
