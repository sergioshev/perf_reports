
window.addEventListener?window.addEventListener('load',so_init,false):window.attachEvent('onload',so_init);
var wait_time = 5000

function so_init(){
	var refresh_time = 0;
	for (i=0; i<6; i++){
		setTimeout("ajaxpage('external/afo_qed_dashboard.html', 'brand_results');  javascript:ajaxpage('external/afo_logo.html', 'brand_logo'); loadobjs('css/afo_page_style.css');", refresh_time);
		refresh_time = refresh_time + wait_time;
		setTimeout("ajaxpage('external/carbookers_qed_dashboard.html', 'brand_results');  javascript:ajaxpage('external/carbookers_logo.html', 'brand_logo'); loadobjs('css/carbookers_page_style.css');", refresh_time);
		refresh_time = refresh_time + wait_time;
		setTimeout("ajaxpage('external/ctix_qed_dashboard.html', 'brand_results');  javascript:ajaxpage('external/ctix_logo.html', 'brand_logo'); loadobjs('css/ctix_page_style.css');", refresh_time);
		refresh_time = refresh_time + wait_time;
		setTimeout("ajaxpage('external/ebuk_qed_dashboard.html', 'brand_results');  javascript:ajaxpage('external/ebuk_logo.html', 'brand_logo'); loadobjs('css/ebuk_page_style.css');", refresh_time);
		refresh_time = refresh_time + wait_time;
		setTimeout("ajaxpage('external/orbz_qed_dashboard.html', 'brand_results');  javascript:ajaxpage('external/orbz_logo.html', 'brand_logo'); loadobjs('css/orbz_page_style.css');", refresh_time);
		refresh_time = refresh_time + wait_time;
		setTimeout("ajaxpage('external/osa_qed_dashboard.html', 'brand_results');  javascript:ajaxpage('external/osa_logo.html', 'brand_logo'); loadobjs('css/osa_page_style.css');", refresh_time);
		refresh_time = refresh_time + wait_time;
	}
	// Redirects to the same page
	window.locationf="qed_performance_dashboard.html";	
}
