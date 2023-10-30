const isPermanent = document.querySelector('input[name="is_permanent"]');
const expDate = document.querySelector('input[name="exp_date"]');

isPermanent.checked = false;

isPermanent.addEventListener("change", () => {
	expDate.disabled = isPermanent.checked;
});
