// Author: Kyle Shanks

function update_progress(pct) {
    if(!isNaN(pct) && pct != null) {
        if(pct > 100) {pct = 100}; // Too High
        if(pct < 0) {pct = 0};     // Too Low
        var offset = (( -parseFloat(pct) /100) * 220) - 220; // Getting offset for the SVG

        $('.progress-bar').attr('stroke-dashoffset',offset);
        $('.progress-label').text(Number(Math.round(pct+'e2')+'e-2')+'%'); // Rounds to two decimal places

        // Check for finish
        (pct === 100)?( complete() ):( incomplete() );
    };
    
};

// Complete and Error States
function complete() { $('.container').addClass('flipped complete').removeClass('error'); };
function incomplete() { $('.container').removeClass('flipped complete'); };
function error() { $('.container').addClass('flipped error').removeClass('complete');  };
function no_error() { $('.container').removeClass('flipped error'); };

// For testing
// function test() {
//     $('.progress-bar').css('transition', '0.12s ease');
//     for(var i = 0; i <= 100; i++) { timer_thing(i); };
//     setTimeout(function(){ $('.progress-bar').css('transition', '0.4s cubic-bezier(0.5,0,0.2,1)'); }, 10100);
// };
// function timer_thing(i) { setTimeout(function(){ update_progress(i) }, (100 * i)); };