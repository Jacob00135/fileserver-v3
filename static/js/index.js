(() => {
    'use strict';

    const searchObj = parseSearch();

    const sortBtn = document.getElementById('sort');
    if (sortBtn !== null) {
        const sortDialog = document.getElementById('sort-dialog');
        const ascendingSelect = sortDialog.querySelector('select[name="ascending"]');

        sortBtn.addEventListener('click', showSortDialog);
        sortDialog.querySelector('select[name="by"]').addEventListener('change', changeAscendingSelect);
        sortDialog.querySelector('button.submit').addEventListener('click', changeSort);        
    }

    function showSortDialog(e) {
        document.getElementById('sort-dialog').showModal();
    }

    function changeAscendingSelect(e) {
        const by = e.target.value;
        const v0 = document.querySelector('#sort-dialog select[name="ascending"] option[value="0"]');
        const v1 = document.querySelector('#sort-dialog select[name="ascending"] option[value="1"]');
        if (by === 'type' || by=== 'name') {
            v0.innerHTML = '降序';
            v1.innerHTML = '升序';
        } else if (by === 'size') {
            v0.innerHTML = '从大到小';
            v1.innerHTML = '从小到大';
        } else if (by === 'date') {
            v0.innerHTML = '从新到旧';
            v1.innerHTML = '从旧到新';
        } else {
            v0.innerHTML = '降序';
            v1.innerHTML = '升序';
        }
    }

    function changeSort(e) {
        const form = document.querySelector('#sort-dialog form');
        searchObj['sort_by'] = form['by'].value;
        searchObj['sort_ascending'] = form['ascending'].value;

        location.href = unparseSearch(location.pathname, searchObj);
    }
})();