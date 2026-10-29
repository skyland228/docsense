const registerForm = document.querySelector("#register-form");
const message = document.querySelector("#message");

registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const submitButton = registerForm.querySelector("button");
    const data = Object.fromEntries(new FormData(registerForm));

    submitButton.disabled = true;
    DocSenseApi.setMessage(message, "Создаём аккаунт...");

    try {
        await DocSenseApi.request("/users", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(data),
        });
        window.location.href = `/?registered=1&username=${encodeURIComponent(data.username)}`;
    } catch (error) {
        DocSenseApi.setMessage(message, error.message, true);
    } finally {
        submitButton.disabled = false;
    }
});
