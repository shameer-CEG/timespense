window.addEventListener("load", function () {
    "use strict";
    // Bootstrap wysihtml5 (note: wysihtml5 is a jQuery plugin, so this won't work without jQuery)
    const editors = document.querySelectorAll(".textarea_editor");
    editors.forEach(editor => {
        // Initialize wysihtml5 for each editor if you have a vanilla JS equivalent or plugin without jQuery.
        // Editor plugin initialization is not converted as it relies on jQuery.
    });
});

window.addEventListener("load", function () {
    // Custom scrollbar (note: mCustomScrollbar is also a jQuery plugin)
    const scrollElements = document.querySelectorAll(".customscroll");
    scrollElements.forEach(elem => {
        // Initialize mCustomScrollbar plugin in vanilla JS if you have an equivalent plugin without jQuery.
    });
});

window.addEventListener("resize", function () {
    const scrollElements = document.querySelectorAll(".customscroll");
    scrollElements.forEach(elem => {
        // Reinitialize or handle resize event logic for scrollbar plugin.
    });
});

document.addEventListener("DOMContentLoaded", function () {
    "use strict";
    
    // Background Image
    document.querySelectorAll(".bg_img").forEach((img) => {
        img.style.display = "none";
        img.parentNode.style.background = `url(${img.getAttribute("src")}) no-repeat center center`;
    });

    // Image to SVG conversion
    document.querySelectorAll("img.svg").forEach((img) => {
        const imgID = img.getAttribute("id");
        const imgClass = img.getAttribute("class");
        const imgURL = img.getAttribute("src");

        fetch(imgURL)
            .then((response) => response.text())
            .then((data) => {
                const parser = new DOMParser();
                const xmlDoc = parser.parseFromString(data, "text/xml");
                let svg = xmlDoc.querySelector("svg");

                if (imgID) svg.setAttribute("id", imgID);
                if (imgClass) svg.setAttribute("class", imgClass + " replaced-svg");

                svg.removeAttribute("xmlns:a");

                if (!svg.hasAttribute("viewBox") && svg.hasAttribute("height") && svg.hasAttribute("width")) {
                    svg.setAttribute("viewBox", `0 0 ${svg.getAttribute("height")} ${svg.getAttribute("width")}`);
                }

                img.parentNode.replaceChild(svg, img);
            });
    });

    // Codeblock escape
    function escapeHtml(string) {
        return String(string).replace(/[&<>"'\/]/g, function (s) {
            return {
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#39;",
                "/": "&#x2F;"
            }[s];
        });
    }

    const codeblocks = document.querySelectorAll("pre code");
    codeblocks.forEach((block) => {
        const html = escapeHtml(block.innerHTML);
        block.innerHTML = html;
        hljs.highlightBlock(block);  // Assuming hljs (highlight.js) is globally available
    });

    // Search icon filter
    document.querySelector("#filter_input").addEventListener("keyup", function () {
        const value = this.value.toLowerCase();
        document.querySelectorAll("#filter_list .fa-hover").forEach((item) => {
            const text = item.textContent.toLowerCase();
            item.style.display = text.includes(value) ? "" : "none";
        });
    });

    // Custom select 2 init
    // Assuming select2 library is globally available
    document.querySelectorAll(".custom-select2").forEach((select) => {
        $(select).select2();  // Requires jQuery for select2 to work
    });

    // Tooltip and popover initialization
    document.querySelectorAll('[data-toggle="tooltip"]').forEach((elem) => {
        new bootstrap.Tooltip(elem);  // Bootstrap Tooltip initialization in vanilla JS
    });

    document.querySelectorAll('[data-toggle="popover"]').forEach((elem) => {
        new bootstrap.Popover(elem);  // Bootstrap Popover initialization in vanilla JS
    });

    // Form-control focus handling
    document.querySelectorAll(".form-control").forEach((input) => {
        input.addEventListener("focus", function () {
            this.parentNode.classList.add("focus");
        });
        input.addEventListener("blur", function () {
            this.parentNode.classList.remove("focus");
        });
    });

    // Sidebar menu icon toggle
    document.querySelectorAll('.menu-icon, [data-toggle="left-sidebar-close"]').forEach((icon) => {
        icon.addEventListener("click", function () {
            document.body.classList.toggle("sidebar-shrink");
            document.querySelector(".left-side-bar").classList.toggle("open");
            document.querySelector(".mobile-menu-overlay").classList.toggle("show");
        });
    });

    document.querySelector('[data-toggle="header_search"]').addEventListener("click", function () {
        document.querySelector(".header-search").classList.toggle("show");
    });

    document.addEventListener("click", function (e) {
        if (!e.target.closest(".left-side-bar") && !e.target.closest(".menu-icon")) {
            document.querySelector(".left-side-bar").classList.remove("open");
            document.querySelector(".mobile-menu-overlay").classList.remove("show");
        }
    });

    // Sidebar menu active class
    const currentPath = window.location.pathname.split("/").pop();
    document.querySelectorAll("#accordion-menu a").forEach((link) => {
        if (link.getAttribute("href") === currentPath) {
            link.classList.add("active");
        }
    });

    // Click to copy icon
    document.querySelectorAll(".fa-hover").forEach((icon) => {
        icon.addEventListener("click", function (event) {
            event.preventDefault();
            const iconHtml = this.querySelector(".icon-copy").outerHTML;
            CopyToClipboard(iconHtml, true, "Copied");
        });
    });

    // Date picker initialization (if using vanilla JS alternatives to datepicker and timeDropper)
    const datePickers = document.querySelectorAll(".date-picker");
    datePickers.forEach((picker) => {
        new Pikaday({ field: picker, format: 'DD MMM YYYY' });
    });

    const timePickers = document.querySelectorAll(".time-picker");
    timePickers.forEach((picker) => {
        // Initialize timepicker logic here
    });

    // Data attributes for styles
    document.querySelectorAll("[data-color]").forEach((elem) => {
        elem.style.color = elem.getAttribute("data-color");
    });

    document.querySelectorAll("[data-bgcolor]").forEach((elem) => {
        elem.style.backgroundColor = elem.getAttribute("data-bgcolor");
    });

    document.querySelectorAll("[data-border]").forEach((elem) => {
        elem.style.border = elem.getAttribute("data-border");
    });

    // Sidebar accordion menu (requires custom vmenuModule logic)
    const accordionMenu = document.querySelector("#accordion-menu");
    vmenuModule(accordionMenu, { Speed: 400, autostart: false, autohide: true });
});

// Copy to Clipboard function
function CopyToClipboard(value, showNotification = true, notificationText = "Copied to clipboard") {
    const tempInput = document.createElement("input");
    document.body.appendChild(tempInput);
    tempInput.value = value;
    tempInput.select();
    document.execCommand("copy");
    document.body.removeChild(tempInput);

    if (showNotification) {
        const notification = document.createElement("div");
        notification.className = "copy-notification";
        notification.textContent = notificationText;
        document.body.appendChild(notification);

        notification.style.display = "block";
        setTimeout(() => {
            notification.style.display = "none";
            notification.remove();
        }, 1000);
    }
}

// Detect IE browser
(function detectIE() {
    const ua = window.navigator.userAgent;

    if (ua.indexOf("MSIE ") > 0 || ua.indexOf("Trident/") > 0) {
        document.body.classList.add("IE");
    }
})();
