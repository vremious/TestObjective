document.addEventListener('DOMContentLoaded', function () {
    const copyEmailButtons = document.querySelectorAll('.copy-email-button');
    copyEmailButtons.forEach(button => {
        button.addEventListener('click', function () {
            const email = button.getAttribute('data-email');
            navigator.clipboard.writeText(email).then(function() {
                alert('Email скопирован в буфер обмена: ' + email);
            }).catch(function(err) {
                console.error('Ошибка при копировании: ', err);
            });
        });
    });
});