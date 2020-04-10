
var gulp = require("gulp"),
    rev = require("gulp-rev"),
    concat = require("gulp-concat"),
    uglify = require("gulp-uglify");

gulp.task('compile', function () {
    "use strict";
    var twig = require("gulp-twig");
    return gulp.src("./src/templates/*.html")
        .pipe(twig({
            title: "Gulp and Twig",
            benefits: [
                'Fast',
                'Flexible',
                'Secure'
            ]
        }))
        .pipe(gulp.dest('./static'));
})

gulp.task("css", function () {
    return gulp.src("./src/static/css/*.css")
        .pipe(gulp.dest("./static/css/"))
})


gulp.task("scripts", function () {
    return gulp.src("./src/static/js/*.js")
                .pipe(gulp.dest("./static/js/"))

})




gulp.task('default', gulp.series('compile', "scripts", "css"));
