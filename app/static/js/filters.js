const programList = document.getElementById("programList");

function showPrograms() {
	programList.classList.remove('hide');
	programList.classList.add('show');
}

function hidePrograms() {
	programList.classList.remove('show');
	programList.classList.add('hide');
}