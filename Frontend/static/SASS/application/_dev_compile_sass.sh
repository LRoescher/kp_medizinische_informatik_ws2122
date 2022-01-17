# compile sass to css every time the sass file is saved

SASS_PATH="..";
CSS_PATH="../../CSS";

sass --watch $SASS_PATH/main.sass:$CSS_PATH/main.css $SASS_PATH/load_batch.sass:$CSS_PATH/load_batch.css $SASS_PATH/analysis.sass:$CSS_PATH/analysis.css $SASS_PATH/person_data.sass:$CSS_PATH/person_data.css $SASS_PATH/result.sass:$CSS_PATH/result.css $SASS_PATH/login.sass:$CSS_PATH/login.css $SASS_PATH/settings.sass:$CSS_PATH/settings.css;

