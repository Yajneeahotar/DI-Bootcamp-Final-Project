function toggleNotifDropdown(e) {
    e.stopPropagation();
    var dropdown = document.getElementById('notifDropdown');
    if (dropdown) dropdown.classList.toggle('open');
}

document.addEventListener('click', function () {
    var dropdown = document.getElementById('notifDropdown');
    if (dropdown) dropdown.classList.remove('open');
});
