document.addEventListener('DOMContentLoaded', () => {

    const textToTypeDiv = document.getElementById('text-to-type');
    const userInput = document.getElementById('user-input');
    const speedSpan = document.getElementById('speed');
    const accuracySpan = document.getElementById('accuracy');
    const keyboardDiv = document.getElementById('keyboard');

    const modeSelect = document.getElementById('mode');
    const difficultySelect = document.getElementById('difficulty');
    const lengthSlider = document.getElementById('length');
    const lengthValue = document.getElementById('length-value');
    const numWordsSlider = document.getElementById('num-words');
    const numWordsValue = document.getElementById('num-words-value');
    const numSentencesSlider = document.getElementById('num-sentences');
    const numSentencesValue = document.getElementById('num-sentences-value');
    const numWordsPerSentenceSlider = document.getElementById('num-words-sentence');
    const numWordsPerSentenceValue = document.getElementById('num-words-sentence-value');
    const newTextButton = document.getElementById('new-text');

    let textToType = '';
    let startTime = null;
    let currentCharIndex = 0;
    let correctChars = 0;
    let incorrectChars = 0;


    function loadText() {
        const mode = modeSelect.value;
        const difficulty = difficultySelect.value;
        const length = lengthSlider.value;
        const numWords = numWordsSlider.value;
        const numSentences = numSentencesSlider.value;
        const numWordsPerSentence = numWordsPerSentenceSlider.value;

        const url = `/api/text?mode=${mode}&difficulty=${difficulty}&length=${length}&num_words=${numWords}&num_sentences=${numSentences}&num_words_per_sentence=${numWordsPerSentence}`;

        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                textToType = data.text;
                displayTestText(textToType);
                createKeyboard();
                resetTyping();
            })
            .catch(error => {
                console.error('Error fetching text:', error);
                textToTypeDiv.textContent = 'Failed to load text. Please try again later.';
            });
    }

    function resetTyping() {
        startTime = null;
        currentCharIndex = 0;
        correctChars = 0;
        incorrectChars = 0;
        userInput.value = '';
        displayTestText(textToType);
        updateKeyboard()
        userInput.focus();
    }

    function displayTestText(text) {
        textToTypeDiv.innerHTML = '';
        for (let i = 0; i < text.length; i++) {
            const charSpan = document.createElement('span');
            charSpan.textContent = text[i];
            textToTypeDiv.appendChild(charSpan);
        }
    }

    userInput.addEventListener('input', () => {
        if (!startTime) {
            startTime = new Date();
        }

        const inputText = userInput.value;
        const inputChars = inputText.split('');

        const textSpans = textToTypeDiv.querySelectorAll('span');
        textSpans.forEach(span => {
            span.classList.remove('correct', 'incorrect', 'current');
        });

        correctChars = 0;
        incorrectChars = 0;


        for (let i = 0; i < textToType.length; i++) {
            if (i < inputChars.length) {
                if (inputChars[i] === textToType[i]) {
                    textSpans[i].classList.add('correct');
                    correctChars++;
                } else {
                    textSpans[i].classList.add('incorrect');
                    incorrectChars++;
                }
            }

            if (i === inputText.length) {
                textSpans[i].classList.add('current');
                currentCharIndex = i;
            }
        }

        const elapsedTime = (new Date() - startTime) / 1000 / 60;
        const typedWords = inputText.length / 5;
        const speed = elapsedTime > 0 ? Math.round(typedWords / elapsedTime) : 0;
        const accuracy = textToType.length > 0 ? Math.round(((textToType.length - incorrectChars) / textToType.length) * 100) : 100;

        speedSpan.textContent = speed;
        accuracySpan.textContent = accuracy;

        sendStats(speed, accuracy);
        updateKeyboard();
    });

    userInput.addEventListener('keydown', (event) => {
        const key = event.key;
        const keyElement = document.querySelector(`.key[data-key="${key.toLowerCase()}"]`);
        if (keyElement) {
            keyElement.classList.add('pressed');
        }
        if (event.key === 'Backspace' && userInput.value.length < currentCharIndex) {
            event.preventDefault();
        }
    });

    userInput.addEventListener('keyup', (event) => {
        const key = event.key;
        const keyElement = document.querySelector(`.key[data-key="${key.toLowerCase()}"]`);
        if (keyElement) {
            keyElement.classList.remove('pressed');
        }
    });


    function sendStats(speed, accuracy) {
        fetch('/api/stats', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ speed: speed, accuracy: accuracy }),
        })
            .then(response => response.json())
            .then(data => console.log('Server response:', data))
            .catch(error => console.error('Error:', error));
    }

    const keyLayout = [
        ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace'],
        ['Tab', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\'],
        ['CapsLock', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', 'Enter'],
        ['Shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 'Shift'],
        ['Ctrl', 'Alt', 'Space']
    ];

    function createKeyboard() {
        keyboardDiv.innerHTML = '';

        for (const row of keyLayout) {
            const rowDiv = document.createElement('div');
            rowDiv.classList.add('keyboard-row');

            for (const key of row) {
                const keyDiv = document.createElement('div');
                keyDiv.classList.add('key');
                keyDiv.textContent = key === 'Space' ? ' ' : key;
                keyDiv.dataset.key = key.toLowerCase();
                rowDiv.appendChild(keyDiv);

                keyDiv.addEventListener('click', () => {
                    if (key.toLowerCase() === 'backspace') {
                        userInput.value = userInput.value.slice(0, -1);

                    } else if (key.toLowerCase() === 'enter') {
                        userInput.value += '\n';
                    }
                    else if (key.toLowerCase() === 'tab') {
                        userInput.value += '\t';
                    }
                    else if (key.toLowerCase() === 'space') {
                        userInput.value += ' ';
                    }
                    else {
                        userInput.value += key;
                    }
                    userInput.focus();
                    userInput.dispatchEvent(new Event('input'));
                });
            }
            keyboardDiv.appendChild(rowDiv);
        }
    }

    function updateKeyboard() {
        const textSpans = textToTypeDiv.querySelectorAll('span');
        const currentKey = textSpans[currentCharIndex] ? textSpans[currentCharIndex].textContent : null
        const keyElements = document.querySelectorAll('.key');
        keyElements.forEach(keyElement => {
            keyElement.classList.remove('current-key');
            const keyText = keyElement.dataset.key;

            if (currentKey && keyText === currentKey.toLowerCase()) {
                keyElement.classList.add('current-key');
            }
        });
    }
    // --- Новая функция для управления видимостью элементов управления ---
    function updateControlVisibility() {
        const selectedMode = modeSelect.value;
        // Сначала скрываем все группы
        document.querySelectorAll('.control-group').forEach(group => {
            group.style.display = 'none';
        });

        // Затем показываем нужные, в зависимости от режима
        document.querySelectorAll(`.${selectedMode}`).forEach(group => {
            group.style.display = 'block'; // Или 'flex', если вы используете flexbox
        })

    }

    // --- Обработчики событий ---

    modeSelect.addEventListener('change', () => {
        updateControlVisibility(); // Обновляем видимость
        loadText(); // Загружаем новый текст
    });

    difficultySelect.addEventListener('change', loadText);

    lengthSlider.addEventListener('input', () => {
        lengthValue.textContent = lengthSlider.value;
    });

    numWordsSlider.addEventListener('input', () => {
        numWordsValue.textContent = numWordsSlider.value;
    });

    numSentencesSlider.addEventListener('input', () => {
        numSentencesValue.textContent = numSentencesSlider.value;
    });

    numWordsPerSentenceSlider.addEventListener('input', () => {
        numWordsPerSentenceValue.textContent = numWordsPerSentenceSlider.value;
    });

    newTextButton.addEventListener('click', loadText);

    // --- Инициализация ---

    updateControlVisibility(); //  Начальная настройка видимости
    loadText();
    userInput.focus();
});