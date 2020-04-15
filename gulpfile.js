
var gulp = require("gulp"),
    rev = require("gulp-rev"),
    clean = require("gulp-clean"),
    revCollector = require("gulp-rev-collector");

var webserver = require("gulp-webserver");

gulp.task("clean", function() {
    return gulp.src("./static")
        .pipe(clean())
})

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



gulp.task("revsion", function () {
    return gulp.src(
        [
            "./src/static/**/*.css",
            "./src/static/**/*.js",
        ],
    )
        .pipe(rev())
        .pipe(gulp.dest('static/'))
        .pipe(rev.manifest())
        .pipe(gulp.dest('static/rev/'))

})


gulp.task("replace", function () {
    return gulp.src(["static/rev/*.json", "static/*.html"])
        .pipe(revCollector({
            replaceReved: true
        }))
        .pipe(gulp.dest("static"));
})


gulp.task('default', gulp.series("clean", "compile", "revsion", "replace", function (done) {
    done();
}));
