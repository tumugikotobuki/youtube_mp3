$(document).ready(function(){
    $('.input-btn').on('click', function(){
        $(this).next().toggleClass('loading');
    })
});