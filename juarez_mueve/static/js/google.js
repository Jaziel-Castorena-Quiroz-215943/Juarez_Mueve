function openGooglePopup(url) {
    const width = 500;
    const height = 600;

    const left = (window.screen.width / 2) - (width / 2);
    const top = (window.screen.height / 2) - (height / 2);

    const popup = window.open(
        url,
        "google_login_popup",
        `width=${width},height=${height},left=${left},top=${top},resizable=yes`
    );

    if (!popup) {
        alert("Por favor permite ventanas emergentes para continuar con el inicio de sesión.");
    }
}

document.getElementById("google-btn")?.addEventListener("click", function() {
    openGooglePopup(this.dataset.url);
});
