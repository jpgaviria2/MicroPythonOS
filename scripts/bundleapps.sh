output=appstore_backend/bundled_apps/
outputjson=appstore_backend/apps.json
output=$(readlink -f "$output")
outputjson=$(readlink -f "$outputjson")

mkdir -p "$output"

rm "$output"/*.mpk
rm "$outputjson"

echo "[" | tee -a "$outputjson"

for apprepo in internal_filesystem/apps internal_filesystem/builtin/apps; do
	echo "Listing apps in $apprepo"
	ls -1 "$apprepo" | while read appdir; do
	    echo "Bundling $apprepo/$appdir"
	    pushd "$apprepo"/"$appdir"
	    manifest=META-INF/MANIFEST.JSON
	    version=$( jq -r '.version' "$manifest" )
            cat "$manifest" | tee -a "$outputjson"
	    echo -n "," | tee -a "$outputjson"
	    mpkname="$output"/"$appdir"_"$version".mpk
	    echo "Creating $mpkname"
	    zip -r0 "$mpkname" .
	    cp res/mipmap-mdpi/icon_64x64.png "$mpkname"_icon_64x64.png
	    popd
	done
done

# remove the last , to have valid json:

truncate -s -1 "$outputjson"

echo "]" | tee -a "$outputjson"
