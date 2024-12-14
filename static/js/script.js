document.addEventListener('DOMContentLoaded', () => {
    const screenContainer = document.querySelector('.screen-container');
    const beginRouteButton = document.getElementById('begin-route');
    const getIdButton = document.getElementById('get-id-btn');
    const userIdInput = document.getElementById('user_id');
    const nextButtons = document.querySelectorAll('.next-button');

    let currentScreenIndex = 0;
    const screens = document.querySelectorAll('.screen');

    // AJAX call to get ID
    getIdButton.addEventListener('click', () => {
        fetch(startRouteURL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: 'get_id=1'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok') {
                const formContainer = document.querySelector('#screen-start .form-container');
                // Remove old message if any
                const oldMessage = formContainer.querySelector('.new-id-message');
                if (oldMessage) oldMessage.remove();
    
                // Create a new message element
                const newMessage = document.createElement('p');
                newMessage.classList.add('new-id-message');
                newMessage.innerHTML = `This is your new ID: <span class="generated-id">${data.new_id}</span>. Please save it carefully.`;
    
                // Insert the new message before the input-row
                const inputRow = formContainer.querySelector('.input-row');
                formContainer.insertBefore(newMessage, inputRow);
            }
        });
    });
    
    beginRouteButton.addEventListener('click', () => {
        const userId = userIdInput.value.trim();
    
        fetch(startRouteURL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `begin_route=1&user_id=${encodeURIComponent(userId)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok') {
                currentScreenIndex = 1;
                slideToScreen(currentScreenIndex);
            } else {
                alert('Error starting route');
            }
        });
    });

    // For each "Next" button on the question screens
    nextButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetId = button.getAttribute('data-next');
            const targetScreen = document.querySelector(targetId);
            const targetIndex = Array.from(screens).indexOf(targetScreen);
            if (targetIndex !== -1) {
                currentScreenIndex = targetIndex;
                slideToScreen(currentScreenIndex);
            }
        });
    });

    function slideToScreen(index) {
        const offset = index * -100; 
        screenContainer.style.transform = `translateY(${offset}vh)`;
    }
});
