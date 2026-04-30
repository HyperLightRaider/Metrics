function bindSlider(id, valueId) {
    const slider = document.getElementById(id);
    const label = document.getElementById(valueId);
    label.textContent = slider.value;
    slider.addEventListener("input", () => {
        label.textContent = slider.value;
    });
}

bindSlider("sleep", "sleepValue");
bindSlider("energy", "energyValue");
bindSlider("mood", "moodValue");
bindSlider("productivity", "productivityValue");

document.getElementById("saveBtn").addEventListener("click", async () => {
    const payload = {
        sleep: document.getElementById("sleep").value,
        energy: document.getElementById("energy").value,
        mood: document.getElementById("mood").value,
        productivity: document.getElementById("productivity").value,
    };

    try {
        const res = await fetch("/save", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        const data = await res.json();
        showToast(data.message || "Сохранено");
    } catch (e) {
        showToast("Ошибка сохранения");
    }
});

function showToast(text) {
    const toast = document.getElementById("toast");
    toast.textContent = text;
    toast.style.display = "block";
    setTimeout(() => {
        toast.style.display = "none";
    }, 2000);
}
