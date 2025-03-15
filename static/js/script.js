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
    const themeToggleButton = document.getElementById('theme-toggle');

    let textToType = '';
    let startTime = null;
    let currentCharIndex = 0;
    let correctChars = 0;
    let incorrectChars = 0;


    // --- Загрузка текста ---
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
                resetTyping(); // Сбрасываем состояние
            })
            .catch(error => {
                console.error('Error fetching text:', error);
                textToTypeDiv.textContent = 'Failed to load text. Please try again later.';
            });
    }

    function displayTestText(text) {
        textToTypeDiv.innerHTML = ''; // Очищаем предыдущий текст
        for (let i = 0; i < text.length; i++) {
            const charSpan = document.createElement('span');
            charSpan.textContent = text[i];
            textToTypeDiv.appendChild(charSpan);
        }
    }
    // --- Сброс состояния ---
    function resetTyping() {
        startTime = null;
        currentCharIndex = 0;
        correctChars = 0;
        incorrectChars = 0;
        userInput.value = '';
        const textSpans = textToTypeDiv.querySelectorAll('span'); //сбрасываем стили
        textSpans.forEach(span => {
            span.classList.remove('correct', 'incorrect', 'current');
        });
        updateKeyboard();
        userInput.focus();
    }

    // --- Обработка ввода ---
    userInput.addEventListener('input', () => {
        if (!startTime) {
            startTime = new Date(); // Фиксируем время начала
        }

        const inputText = userInput.value;
        const inputChars = inputText.split(''); // Массив введенных символов

        const textSpans = textToTypeDiv.querySelectorAll('span');
        textSpans.forEach(span => {  //сбрасываем стили
            span.classList.remove('correct', 'incorrect', 'current');
        });

        correctChars = 0;
        incorrectChars = 0;

        // Сравниваем введенный текст с образцом *посимвольно*
        for (let i = 0; i < textToType.length; i++) {
            if (i < inputChars.length) { // Если символ введен
                if (inputChars[i] === textToType[i]) { // Если символ введен правильно
                    textSpans[i].classList.add('correct'); // Добавляем класс correct
                    correctChars++;
                } else {
                    textSpans[i].classList.add('incorrect'); // Добавляем класс incorrect
                    incorrectChars++;
                }
            }
            if (i === inputText.length) { // Подсвечиваем текущий символ
                textSpans[i].classList.add('current');
                currentCharIndex = i; //обновляем индекс
            }
        }

        // --- Проверка на завершение сеанса (по длине) ---
        if (inputText.length >= textToType.length) {
            // Если длина введенного текста >= длине текста для печати
            const endTime = new Date();
            const elapsedTime = (endTime - startTime) / 1000 / 60; // Время в минутах
            const typedWords = inputText.length / 5;
            const speed = elapsedTime > 0 ? Math.round(typedWords / elapsedTime) : 0;
            const accuracy = textToType.length > 0 ? Math.round(((textToType.length - incorrectChars) / textToType.length) * 100) : 100;
            // Отправляем статистику
            sendStats(speed, accuracy);
            // Загружаем новый текст
            loadText();
            return; // !!! ВАЖНО !!! Выходим из обработчика
        }


        // Обновляем статистику (если сеанс не завершен)
        const elapsedTime = (new Date() - startTime) / 1000 / 60;
        const typedWords = inputText.length / 5;
        const speed = elapsedTime > 0 ? Math.round(typedWords / elapsedTime) : 0;
        const accuracy = textToType.length > 0 ? Math.round(((textToType.length - incorrectChars) / textToType.length) * 100) : 100;

        speedSpan.textContent = speed;
        accuracySpan.textContent = accuracy;
        updateKeyboard();
    });
    // --- Функции ---
    userInput.addEventListener('keydown', (event) => { //добавляем обработчик нажатия
        const key = event.key; // Получаем нажатую клавишу
        const keyElement = document.querySelector(`.key[data-key="${key.toLowerCase()}"]`); //ищем клавишу
        if (keyElement) { //если клавиша найдена
            keyElement.classList.add('pressed'); //добавляем класс
        }
    });

    userInput.addEventListener('keyup', (event) => { //обработчик отпускания клавиш
        const key = event.key;
        const keyElement = document.querySelector(`.key[data-key="${key.toLowerCase()}"]`);
        if (keyElement) {
            keyElement.classList.remove('pressed'); // Убираем класс при отпускании
        }
    });

    function sendStats(speed, accuracy) {
        const mode = modeSelect.value;
        const difficulty = difficultySelect.value;
        const length = textToType.length;
        fetch('/api/stats', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ speed: speed, accuracy: accuracy, mode: mode, difficulty: difficulty, length: length }),
        })
            .then(response => response.json())
            .then(data => console.log('Server response:', data))
            .catch(error => console.error('Error:', error));
    }

    // --- Виртуальная клавиатура ---
    const keyLayout = [
        ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace'],
        ['Tab', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\'],
        ['CapsLock', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', 'Enter'],
        ['Shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 'Shift'],
        ['Ctrl', 'Alt', 'Space']
    ];

    function createKeyboard() {
        keyboardDiv.innerHTML = ''; // Очищаем клавиатуру

        for (const row of keyLayout) {
            const rowDiv = document.createElement('div');
            rowDiv.classList.add('keyboard-row');

            for (const key of row) {
                const keyDiv = document.createElement('div');
                keyDiv.classList.add('key');
                keyDiv.textContent = key === 'Space' ? ' ' : key; // Вместо Space отображаем пробел
                keyDiv.dataset.key = key.toLowerCase(); // data-атрибут для связи с event.key
                rowDiv.appendChild(keyDiv);

                // Добавляем обработчик клика (для эмуляции нажатия)
                keyDiv.addEventListener('click', () => {
                    if (key.toLowerCase() === 'backspace') {
                        userInput.value = userInput.value.slice(0, -1); // Удаляем последний символ

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
                        userInput.value += key; // Добавляем символ в поле ввода
                    }
                    userInput.focus(); // Возвращаем фокус на поле ввода
                    userInput.dispatchEvent(new Event('input')); // Вызываем событие 'input' вручную
                });
            }
            keyboardDiv.appendChild(rowDiv);
        }
    }
    function updateKeyboard() {
        const textSpans = textToTypeDiv.querySelectorAll('span');
        const currentKey = textSpans[currentCharIndex] ? textSpans[currentCharIndex].textContent : null //получаем текущий символ
        const keyElements = document.querySelectorAll('.key'); //получаем все клавиши
        keyElements.forEach(keyElement => { //проходим по всем клавишам
            keyElement.classList.remove('current-key'); //убираем подсветку со всех клавиш
            const keyText = keyElement.dataset.key; // Сравниваем lowercase

            if (currentKey && keyText === currentKey.toLowerCase()) {
                keyElement.classList.add('current-key');
            }
        });
    }

    function updateControlVisibility() {
        const selectedMode = modeSelect.value;
        document.querySelectorAll('.control-group').forEach(group => {
            group.style.display = 'none';
        });

        document.querySelectorAll(`.${selectedMode}`).forEach(group => {
            group.style.display = 'block'; // Или 'flex', если вы используете flexbox
        })
    }

    modeSelect.addEventListener('change', () => {
        updateControlVisibility();
        loadText();
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

    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.classList.add(savedTheme); // Применяем сохраненную тему
    }

    themeToggleButton.addEventListener('click', () => {
        // Переключаем класс dark-mode у body
        document.body.classList.toggle('dark-mode');

        // Сохраняем текущую тему в localStorage
        if (document.body.classList.contains('dark-mode')) {
            localStorage.setItem('theme', 'dark-mode');
        } else {
            localStorage.setItem('theme', ''); // Если светлая тема, сохраняем пустую строку
        }
    });

    updateControlVisibility();
    loadText();
    userInput.focus();
});