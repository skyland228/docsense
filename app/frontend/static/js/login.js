const loginForm = document.querySelector("#login-form");
const message = document.querySelector("#message");
const pageParams = new URLSearchParams(window.location.search);

if (pageParams.get("registered") === "1") {
    loginForm.elements.username.value = pageParams.get("username") || "";
    DocSenseApi.setMessage(message, "Аккаунт создан. Теперь войдите.");
}

if (DocSenseApi.getToken()) {
    window.location.href = "/app/documents";
}

loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const submitButton = loginForm.querySelector("button");
    const formData = new FormData(loginForm);
    const body = new URLSearchParams();
    body.set("username", formData.get("username"));
    body.set("password", formData.get("password"));

    submitButton.disabled = true;
    DocSenseApi.setMessage(message, "Выполняется вход...");

    try {
        const response = await DocSenseApi.request("/login", {
            method: "POST",
            headers: {"Content-Type": "application/x-www-form-urlencoded"},
            body,
        });
        const result = await response.json();
        DocSenseApi.saveSession(result.access_token, formData.get("username"));
        window.location.href = "/app/documents";
    } catch (error) {
        DocSenseApi.setMessage(message, error.message, true);
    } finally {
        submitButton.disabled = false;
    }
});
