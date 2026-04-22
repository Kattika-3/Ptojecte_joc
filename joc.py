import http.server
import socketserver
import webbrowser
import threading
import time
import os

PORT = 8000
HTML_FILE = "index.html"

# Contingut del joc (HTML + CSS + JS) en un sol bloc
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ca">
<head>
    <meta charset="UTF-8">
    <title>Penjat Pink Edition 🌸</title>
    <style>
        :root {
            --pink-bright: #ff007f;
            --pink-soft: #ff66b2;
            --pink-pale: #ffc0cb;
            --bg-dark: #1a0a12;
            --card-bg: #2d161f;
        }
        body {
            background-color: var(--bg-dark);
            color: white;
            font-family: 'Segoe UI', Roboto, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            overflow: hidden;
        }
        .container {
            background: var(--card-bg);
            padding: 2.5rem;
            border-radius: 25px;
            box-shadow: 0 0 30px rgba(255, 0, 127, 0.3);
            border: 1px solid rgba(255, 102, 178, 0.2);
            text-align: center;
            max-width: 650px;
            width: 90%;
            transition: 0.5s;
        }
        h1 {
            color: var(--pink-bright);
            text-transform: uppercase;
            letter-spacing: 4px;
            text-shadow: 0 0 15px var(--pink-bright);
            margin-bottom: 30px;
        }
        #category-screen { display: block; }
        #game-screen { display: none; }

        .category-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .cat-btn {
            background: rgba(45, 22, 31, 0.6);
            border: 2px solid var(--pink-soft);
            color: white;
            padding: 25px 15px;
            border-radius: 20px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            font-size: 1rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            box-shadow: inset 0 0 15px rgba(255, 0, 127, 0.1);
        }
        .cat-icon {
            font-size: 3.5rem;
            margin-bottom: 15px;
            filter: drop-shadow(0 0 10px var(--pink-bright));
            transition: 0.3s;
        }
        .cat-btn:hover {
            background: rgba(255, 0, 127, 0.15);
            border-color: var(--pink-bright);
            box-shadow: 0 0 30px var(--pink-bright), inset 0 0 20px var(--pink-bright);
            transform: translateY(-10px) scale(1.05);
        }
        .cat-btn:hover .cat-icon {
            filter: drop-shadow(0 0 20px var(--pink-bright)) brightness(1.2);
            transform: rotate(-5deg);
        }
        .cat-label {
            text-transform: uppercase;
            letter-spacing: 2px;
            text-shadow: 0 0 5px white;
        }

        /* Animació de les flors de celebració */
        .flower {
            position: fixed;
            top: -50px;
            font-size: 2rem;
            z-index: 1000;
            pointer-events: none;
            animation: fall linear forwards;
        }

        @keyframes fall {
            to {
                transform: translateY(110vh) rotate(360deg);
            }
        }

        #hangman-svg {
            width: 180px;
            height: 180px;
            margin: 10px;
        }
        .word-display {
            font-size: 2.5rem;
            letter-spacing: 12px;
            margin: 20px 0;
            font-family: 'Courier New', monospace;
            color: var(--pink-pale);
            text-shadow: 0 0 8px var(--pink-soft);
        }
        .keyboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(45px, 1fr));
            gap: 8px;
            margin-top: 20px;
        }
        .key-btn {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--pink-soft);
            color: var(--pink-pale);
            padding: 12px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            transition: 0.2s;
        }
        .key-btn:hover:not(:disabled) {
            background: var(--pink-soft);
            color: white;
            box-shadow: 0 0 12px var(--pink-soft);
        }
        .key-btn:disabled {
            opacity: 0.2;
            cursor: not-allowed;
        }
        .status {
            margin: 10px;
            font-size: 1.3rem;
            color: var(--pink-soft);
        }
        .modal {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.85);
            display: none;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 100;
        }
        .modal-content {
            background: var(--card-bg);
            padding: 3rem;
            border-radius: 25px;
            border: 2px solid var(--pink-bright);
            text-align: center;
            box-shadow: 0 0 40px var(--pink-bright);
        }
        .btn-reset {
            background: var(--pink-bright);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 10px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 20px;
            font-size: 1.1rem;
        }
    </style>
</head>
<body>

    <div class="container" id="category-screen">
        <h1>🌸 PENJAT 🌸</h1>
        <p>Tria una categoria per començar:</p>
        <div class="category-grid" id="category-buttons"></div>
    </div>

    <div class="container" id="game-screen">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h1 id="game-title" style="margin: 0;">JOC</h1>
            <button onclick="toggleMusic()" id="mute-btn" style="background: none; border: none; font-size: 1.5rem; cursor: pointer;">🔊</button>
        </div>
        <div id="cat-indicator" style="color: var(--pink-soft); margin-bottom: 10px; font-weight: bold;"></div>
        
        <svg id="hangman-svg" viewBox="0 0 100 100">
            <line x1="10" y1="90" x2="90" y2="90" stroke="#444" stroke-width="3" />
            <line x1="30" y1="90" x2="30" y2="10" stroke="#444" stroke-width="3" />
            <line x1="30" y1="10" x2="70" y2="10" stroke="#444" stroke-width="3" />
            <line x1="70" y1="10" x2="70" y2="25" stroke="#444" stroke-width="3" />
            
            <circle id="head" cx="70" cy="35" r="8" stroke="white" stroke-width="2" fill="none" style="display:none" />
            <line id="body" x1="70" y1="43" x2="70" y2="65" stroke="white" stroke-width="2" style="display:none" />
            <line id="l-arm" x1="70" y1="50" x2="55" y2="40" stroke="white" stroke-width="2" style="display:none" />
            <line id="r-arm" x1="70" y1="50" x2="85" y2="40" stroke="white" stroke-width="2" style="display:none" />
            <line id="l-leg" x1="70" y1="65" x2="55" y2="80" stroke="white" stroke-width="2" style="display:none" />
            <line id="r-leg" x1="70" y1="65" x2="85" y2="80" stroke="white" stroke-width="2" style="display:none" />
        </svg>

        <div class="status">Vides: <span id="lives">6</span></div>
        <div id="wordDisplay" class="word-display">_ _ _ _ _</div>
        <div id="keyboard" class="keyboard"></div>
        <button class="btn-reset" onclick="location.reload()" style="background: transparent; border: 1px solid var(--pink-soft); padding: 5px 15px; font-size: 0.8rem;">Tornar enrere</button>
    </div>

    <div id="modal" class="modal">
        <div class="modal-content">
            <h2 id="modal-title">RESULTAT</h2>
            <p id="modal-msg"></p>
            <button class="btn-reset" onclick="location.reload()">JUGAR DE NOU</button>
        </div>
    </div>

    <!-- Àudio -->
    <audio id="bg-music" loop>
        <source src="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3" type="audio/mpeg">
    </audio>
    <audio id="win-sound">
        <source src="https://cdn.pixabay.com/audio/2021/08/04/audio_bbd1341065.mp3" type="audio/mpeg">
    </audio>
    <audio id="lose-sound">
        <source src="https://cdn.pixabay.com/audio/2022/03/10/audio_24e370a9b3.mp3" type="audio/mpeg">
    </audio>

    <script>
        const CATEGORIES = {
            "COLORS": { words: ["VERMELL", "BLAU", "VERD", "GROC", "TARONJA", "LILA", "BLANC", "NEGRE", "MARRO", "ROSA"], icon: "🎨" },
            "ANIMALS": { words: ["ELEFANT", "GIRAFA", "LLEO", "TIGRE", "GOS", "GAT", "CAVALL", "OCELL", "SERP", "BALENA"], icon: "🦁" },
            "PEL·LÍCULES": { words: ["BATMAN", "AVATAR", "TITANIC", "SHREK", "GLADIATOR", "ALIEN", "STARWARS", "FROZEN", "JOKER"], icon: "🎬" },
            "MENJAR": { words: ["PIZZA", "PASTA", "HAMBURGUESA", "AMANIDA", "TRUITA", "PAELLA", "SUSHI", "ARROS", "GELAT"], icon: "🍕" },
            "PAÏSOS": { words: ["CATALUNYA", "ESPANYA", "FRANCA", "ITALIA", "ALEMANYA", "JAPO", "MEXIC", "EGIPTE", "BRASIL"], icon: "🌍" },
            "PROFESSIONS": { words: ["METGE", "MESTRE", "CUINER", "PINTOR", "BOMBER", "POLICIA", "ACTOR", "MUSIC", "ADVOCAT"], icon: "👷" },
            "ESPORTS": { words: ["FUTBOL", "BÀSQUET", "TENNIS", "NATACIÓ", "CICLISME", "HOQUEI", "JUDO", "KARATE", "PADEL"], icon: "🏀" },
            "FRUITES": { words: ["POMA", "PERA", "PLATAN", "MADUIXA", "TARONJA", "RAÏM", "PINYA", "LLIMONA", "CIRERA"], icon: "🍎" }
        };

        let secretWord = "";
        let guessedLetters = [];
        let lives = 6;
        const bodyParts = ["head", "body", "l-arm", "r-arm", "l-leg", "r-leg"];

        const music = document.getElementById('bg-music');
        const winSound = document.getElementById('win-sound');
        const loseSound = document.getElementById('lose-sound');
        music.volume = 0.2;

        function toggleMusic() {
            if (music.paused) {
                music.play();
                document.getElementById('mute-btn').innerText = "🔊";
            } else {
                music.pause();
                document.getElementById('mute-btn').innerText = "🔇";
            }
        }

        function initCategories() {
            const container = document.getElementById('category-buttons');
            Object.keys(CATEGORIES).forEach(cat => {
                const btn = document.createElement('button');
                btn.className = 'cat-btn';
                btn.innerHTML = `<div class="cat-icon">${CATEGORIES[cat].icon}</div><div class="cat-label">${cat}</div>`;
                btn.onclick = () => startGame(cat);
                container.appendChild(btn);
            });
        }

        function startGame(category) {
            document.getElementById('category-screen').style.display = 'none';
            document.getElementById('game-screen').style.display = 'block';
            document.getElementById('cat-indicator').innerText = "Categoria: " + category + " " + CATEGORIES[category].icon;
            
            // Iniciar música
            music.play().catch(() => console.log("L'àudio requereix interacció"));

            const words = CATEGORIES[category].words;
            secretWord = words[Math.floor(Math.random() * words.length)];
            
            updateDisplay();
            createKeyboard();
        }

        function createKeyboard() {
            const kb = document.getElementById('keyboard');
            kb.innerHTML = "";
            "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ".split('').forEach(l => {
                const btn = document.createElement('button');
                btn.className = 'key-btn';
                btn.innerText = l;
                btn.onclick = () => guess(l);
                kb.appendChild(btn);
            });
        }

        function guess(letter) {
            if (guessedLetters.includes(letter)) return;
            guessedLetters.push(letter);
            
            const buttons = document.querySelectorAll('.keyboard button');
            buttons.forEach(b => { if(b.innerText === letter) b.disabled = true; });

            if (!secretWord.includes(letter)) {
                lives--;
                document.getElementById(bodyParts[5 - lives]).style.display = "block";
                document.getElementById('lives').innerText = "❤️".repeat(lives) + "🖤".repeat(6-lives);
            }

            updateDisplay();
            checkGame();
        }

        function updateDisplay() {
            const display = secretWord.split('').map(l => guessedLetters.includes(l) ? l : "_").join(' ');
            document.getElementById('wordDisplay').innerText = display;
        }

        function createFlowerRain() {
            const flowers = ['🌸', '🌺', '🌷', '🌹', '💮'];
            for (let i = 0; i < 50; i++) {
                setTimeout(() => {
                    const flower = document.createElement('div');
                    flower.className = 'flower';
                    flower.innerText = flowers[Math.floor(Math.random() * flowers.length)];
                    flower.style.left = Math.random() * 100 + 'vw';
                    flower.style.animationDuration = (Math.random() * 3 + 2) + 's';
                    flower.style.opacity = Math.random();
                    flower.style.fontSize = (Math.random() * 20 + 20) + 'px';
                    document.body.appendChild(flower);
                    
                    // Eliminar la flor després de l'animació
                    setTimeout(() => flower.remove(), 5000);
                }, i * 100);
            }
        }

        function checkGame() {
            if (!document.getElementById('wordDisplay').innerText.includes("_")) {
                music.pause();
                winSound.play();
                createFlowerRain();
                showModal("🌸 VICTÒRIA! 🌸", "Felicitats! Has salvat el penjat!", true);
            } else if (lives <= 0) {
                music.pause();
                loseSound.play();
                showModal("💀 OH NO...", "La paraula era: " + secretWord, false);
            }
        }

        function showModal(title, msg, isWin) {
            const modalContent = document.querySelector('.modal-content');
            modalContent.style.borderColor = isWin ? 'var(--pink-bright)' : '#555';
            modalContent.style.boxShadow = isWin ? '0 0 50px var(--pink-bright)' : '0 0 20px #000';
            
            const titleElem = document.getElementById('modal-title');
            titleElem.innerText = title;
            titleElem.style.color = isWin ? 'var(--pink-bright)' : '#888';
            
            document.getElementById('modal-msg').innerText = msg;
            document.getElementById('modal').style.display = "flex";
        }

        initCategories();
    </script>
</body>
</html>
"""

def start_server():
    handler = http.server.SimpleHTTPRequestHandler
    # Permitir reutilización de dirección para evitar errores de puerto ocupado si se reinicia rápido
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"✅ Servidor actiu a http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)

    print("\n🚀 Iniciant el nou Joc del Penjat PINK Edition...")
    
    thread = threading.Thread(target=start_server, daemon=True)
    thread.start()

    time.sleep(1)
    webbrowser.open(f"http://localhost:{PORT}")

    print("👉 Prem CTRL+C per tancar el joc.\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Joc tancat.")
        if os.path.exists(HTML_FILE):
            os.remove(HTML_FILE)
