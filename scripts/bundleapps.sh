output=/home/user/projects/MicroPythonOS/apps/
outputjson="$output"/app_index.json
output=$(readlink -f "$output")
outputjson=$(readlink -f "$outputjson")

#mpks="$output"/mpks/
#icons="$output"/icons/

mkdir -p "$output"
#mkdir -p "$mpks"
#mkdir -p "$icons"

#rm "$output"/*.mpk
#rm "$output"/*.png
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
            thisappdir="$output"/"$appdir"
            mkdir -p "$thisappdir"
            mkdir -p "$thisappdir"/mpks
            mkdir -p "$thisappdir"/icons
	    mpkname="$thisappdir"/mpks/"$appdir"_"$version".mpk
	    echo "Creating $mpkname"
	    zip -r0 "$mpkname" .
	    cp res/mipmap-mdpi/icon_64x64.png "$thisappdir"/icons/"$appdir"_"$version"_64x64.png
	    popd
	done
done

# remove the last , to have valid json:

truncate -s -1 "$outputjson"

echo "]" | tee -a "$outputjson"
