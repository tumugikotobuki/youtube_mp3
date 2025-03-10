// // ボタンクリック確認
// document.getElementById('input-btn').onclick = function() {
//     alert('Hello');
// }


document.getElementById('input-btn').onclick = function() {
    
};
// 変換時のローディングアニメーション
$(document).ready(function(){
    $('.convert-btn').on('click', function(){
        $('#loading').addClass('loading');
        setTimeout(function(){
            $('.loading').removeClass('loading');}, 7000);
        $('#loading-item').addClass('loading-item');
        setTimeout(function(){
            $('.loading-item').removeClass('loading-item');}, 7000);
    });
});