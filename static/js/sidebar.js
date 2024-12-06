document.getElementById('sidebar').classList.add('active');
document.getElementById('content').classList.add('active');
document.getElementById('overlay').classList.remove('active');

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('active');
    document.getElementById('content').classList.toggle('active');
    document.getElementById('overlay').classList.toggle('active');


}

// toggleSidebar()
// Initial execution
// Attach the function to the window's resize event
// window.addEventListener('resize', toggleSidebar);
// Toggle sidebar when the button is clicked
document.getElementById('menu-toggle').addEventListener('click', toggleSidebar);
document.getElementById('overlay').addEventListener('click', toggleSidebar);