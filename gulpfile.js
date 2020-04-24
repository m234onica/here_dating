
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

gulp.task("webserver", function() {
    setTimeout(function () {
        gulp.src("static")                   // 預設開啟路徑
            .pipe(webserver({                     // 啟動 webserver
                livereload: true,                   // Livereload 的功能
                open: false,                        // 是否自動開啟 瀏覽器
                host: '0.0.0.0',                    // 如果使用 0.0.0.0 的 ip，還會另外開啟 wifi 等對外網路
                port: 5001,                        // 開放通訊埠
            }));
    }, 1000);
})

gulp.task('default', gulp.series("clean", "compile", "revsion", "replace", function (done) {
    done();
}));
