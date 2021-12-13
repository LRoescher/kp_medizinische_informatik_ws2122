# compile sass to css every time the sass file is saved

SASS_PATH="..";
CSS_PATH="../../CSS";

./dart-sass/sass --watch $SASS_PATH/main.sass:$CSS_PATH/main.css $SASS_PATH/load_batch.sass:$CSS_PATH/load_batch.css $SASS_PATH/batch_summary.sass:$CSS_PATH/batch_summary.css $SASS_PATH/person_data.sass:$CSS_PATH/person_data.css $SASS_PATH/result.sass:$CSS_PATH/result.css;

