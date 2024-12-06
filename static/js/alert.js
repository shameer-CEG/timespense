document.addEventListener("DOMContentLoaded", function () {
    // Get the alert element
    const alertElement = document.getElementById("auto-dismiss-alert");
    console.log(alertElement);
    // Check if the alert element exists
    if (alertElement) {
        // Set a timeout to hide the alert after 5 seconds (5000 milliseconds)
        setTimeout(function () {
            // Hide the alert
            alertElement.style.display = "none";
        }, 5000);
    }
});
