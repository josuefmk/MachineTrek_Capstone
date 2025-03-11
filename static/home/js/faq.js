function toggleAnswer(button) {
    const answer = button.nextElementSibling;
    answer.style.display = (answer.style.display === "block") ? "none" : "block";
    button.classList.toggle("active");
}