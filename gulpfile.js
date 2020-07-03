
var gulp = require("gulp"),
    imagemin = require("gulp-imagemin"),
    fs = require("fs");

var version = "static-v1";

gulp.task('compile', function (done) {
    "use strict";
    var twig = require("gulp-twig");
    var data = JSON.parse(fs.readFileSync("./src/static/data/text.json"))

    gulp.src("./src/templates/pair.html")
        .pipe(twig({
            data: {
                pair: data.pair
            }
        }))
        .pipe(gulp.dest("./doc/" + version))

    gulp.src("./src/templates/message.html")
        .pipe(twig({
            data: {
                message: data.message
            }
        }))
        .pipe(gulp.dest("./doc/" + version))

    gulp.src("./src/templates/rule.html")
        .pipe(twig(
            {
                data: {
                    rule: data.rule
                }
            }
        ))
        .pipe(gulp.dest("./doc/" + version))

    done();
    return "done"
})


gulp.task("pack_js_css", function() {
    return gulp.src(
        [
            "./src/static/**/*.css",
            "./src/static/**/config.js",
            "./src/static/**/extension.js",
        ]
    ).pipe(gulp.dest("./doc/" + version))
})


gulp.task("imagemin", function () {
    return gulp.src("./src/static/images/**/*")
        .pipe(imagemin())
        .pipe(gulp.dest("./doc/" + version + "/images/"))

})



gulp.task("webserver", function () {
    setTimeout(function () {
        gulp.src("doc")                   // 預設開啟路徑
            .pipe(webserver({                     // 啟動 webserver
                livereload: true,                   // Livereload 的功能
                open: false,                        // 是否自動開啟 瀏覽器
                host: '0.0.0.0',                    // 如果使用 0.0.0.0 的 ip，還會另外開啟 wifi 等對外網路
                port: 5001,                        // 開放通訊埠
            }));
    }, 1000);
})


gulp.task('default', gulp.series("compile", "pack_js_css", "imagemin", function (done) {
    done();
}));

