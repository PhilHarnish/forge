const gulp = require('gulp');
const jasmine = require('gulp-jasmine');

const paths = {
  scripts: [
    'src/folding/*.js',
    'src/util/*.js',
    'src/util/set/*.js',
  ],
  specs: [
    'spec/folding/*.js',
    'spec/util/*.js',
    'spec/util/set/*.js',
  ],
};
paths.combined = paths.scripts.concat(paths.specs);

// Tests.
gulp.task('specs', () => {
  return gulp.src(paths.specs).pipe(jasmine());
});

// Rerun the tests when a file changes.
gulp.task('watch', () => {
  gulp.watch(paths.combined, ['specs']);
});

// Default task.
gulp.task('default', ['specs']);
