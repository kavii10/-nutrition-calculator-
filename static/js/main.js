window.addEventListener('DOMContentLoaded', () => {
    const searchBtn = document.getElementById('search-btn');
    const recipeInput = document.getElementById('recipe-input');
    const resultContainer = document.getElementById('result-container');
    const errorMsg = document.getElementById('error-msg');

    searchBtn.addEventListener('click', () => {
        clearResults();
        const recipe = recipeInput.value.trim();
        if (!recipe) {
            errorMsg.textContent = 'Please enter a recipe name.';
            return;
        }
        fetchNutrition(recipe);
    });

    function clearResults() {
        errorMsg.textContent = '';
        resultContainer.innerHTML = '';
    }

    async function fetchNutrition(recipeName) {
        try {
            const response = await fetch(`/nutrition?recipe=${encodeURIComponent(recipeName)}`);
            const data = await response.json();
            if (!response.ok) {
                errorMsg.textContent = data.error || 'Error fetching nutrition data.';
                return;
            }
            renderNutrition(data);
        } catch (error) {
            errorMsg.textContent
