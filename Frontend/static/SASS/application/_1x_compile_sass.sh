
SASS_PATH=".."
CSS_PATH="../../CSS"

./dart-sass/sass $SASS_PATH/main.sass $CSS_PATH/main.css
./dart-sass/sass $SASS_PATH/load_batch.sass $CSS_PATH/load_batch.css
./dart-sass/sass $SASS_PATH/analysis.sass $CSS_PATH/analysis.css
./dart-sass/sass $SASS_PATH/person_data.sass $CSS_PATH/person_data.css
./dart-sass/sass $SASS_PATH/result.sass $CSS_PATH/result.css
./dart-sass/sass $SASS_PATH/login.sass $CSS_PATH/login.css


#./sass --watch ../Frontend/static/SASS/main.sass ../Frontend/static/CSS/main.css