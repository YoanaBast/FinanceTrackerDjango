document.addEventListener('DOMContentLoaded', () => {
  try {
    const meta = document.getElementById('page-meta');
    if (!meta) {
      console.error('page-meta not found');
      return;
    }

    const addCategoryUrl = meta.dataset.addCategoryUrl;
    const pageType = meta.dataset.pageType || 'expense';

    const toggleBtn = document.getElementById('show-add-category');
    const container = document.getElementById('add-category-container');
    const formElement = document.getElementById('add-category-form');

    // Toggle add-category form visibility
    if (toggleBtn && container) {
      toggleBtn.addEventListener('click', () => {
        container.style.display = container.style.display === 'none' ? 'block' : 'none';
      });
    }

    if (!formElement) return;

    formElement.addEventListener('submit', async (e) => {
      e.preventDefault();
      const nameInput = document.getElementById('category-name');
      const name = nameInput?.value.trim();
      if (!name) return alert('Category name cannot be empty');

      const csrfEl = document.querySelector('[name=csrfmiddlewaretoken]');
      const csrfToken = csrfEl ? csrfEl.value : '';

      try {
        const res = await fetch(addCategoryUrl, {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          body: new URLSearchParams({ name, type: pageType })
        });

        const data = await res.json();

        if (data.success) {
          const select = document.querySelector('select[name="category"]');
          if (!select) return alert('Category added but <select> not found.');

          // Add the new category as a valid choice
          const option = document.createElement('option');
          option.value = data.id;
          option.text = data.name;
          option.selected = true;
          select.add(option);

          nameInput.value = '';
          container.style.display = 'none';
        } else {
          alert('Error adding category: ' + JSON.stringify(data.error || data));
        }
      } catch (err) {
        console.error('Error adding category', err);
        alert('Network error while adding category.');
      }
    });

  } catch (err) {
    console.error('category.js top-level error', err);
  }
});
