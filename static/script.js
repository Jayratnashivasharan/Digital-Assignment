document.querySelector(".upload-form")?.addEventListener("submit", () => {
    const btn = document.querySelector(".submit-btn");
    btn.innerText = "⏳ Uploading...";
    btn.disabled = true;
    btn.style.opacity = "0.7";
});
