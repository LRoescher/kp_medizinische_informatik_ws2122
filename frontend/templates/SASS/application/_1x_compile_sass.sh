
SASS_PATH=".."
CSS_PATH="../../CSS"

./dart-sass/sass $SASS_PATH/main.sass $CSS_PATH/main.css
./dart-sass/sass $SASS_PATH/load_batch.sass $CSS_PATH/load_batch.css
./dart-sass/sass $SASS_PATH/batch_summary.sass $CSS_PATH/batch_summary.css
./dart-sass/sass $SASS_PATH/person_data.sass $CSS_PATH/person_data.css
./dart-sass/sass $SASS_PATH/result.sass $CSS_PATH/result.css


#./sass --watch ../Frontend/static/SASS/main.sass ../Frontend/static/CSS/main.css