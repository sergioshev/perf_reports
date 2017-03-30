
window.addEventListener?window.addEventListener('load',so_init,false):window.attachEvent('onload',so_init);


function so_init(){
	setTimeout("ajaxpage('external/orbz_qed_page.html', 'brand_results');  javascript:ajaxpage('external/orbz_logo.html', 'brand_logo'); loadobjs('css/orbz_page_style.css');", 0);	
}
