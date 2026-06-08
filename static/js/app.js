document.addEventListener('DOMContentLoaded', function () {

    const toggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');

    toggle.addEventListener('click', function () {

        sidebar.classList.toggle('d-none');

    });

});