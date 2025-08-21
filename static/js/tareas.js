// static/js/tareas.js
document.querySelectorAll('.btn-edit').forEach(btn => {
    btn.addEventListener('click', () => {
        const form = btn.closest('.tarea-form');
        const view = form.querySelector('.tarea-view');
        const edit = form.querySelector('.tarea-edit');
        const saveBtn = form.querySelector('.btn-save');

        view.classList.add('d-none');
        edit.classList.remove('d-none');
        btn.classList.add('d-none');
        saveBtn.classList.remove('d-none');
    });
});
