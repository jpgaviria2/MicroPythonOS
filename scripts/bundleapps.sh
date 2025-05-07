output=appstore_backend/bundled_apps/
output=$(readlink -f "$output")
mkdir -p "$output"
rm "$output"/*.mpk

for apprepo in internal_filesystem/apps internal_filesystem/builtin/apps; do
	echo "Listing apps in $apprepo"
	ls -1 "$apprepo" | while read appdir; do
	    echo "Bundling $apprepo/$appdir"
	    pushd "$apprepo"/"$appdir"
	    version=$( grep "^Version:" META-INF/MANIFEST.MF | cut -d " " -f 2)
	    mpkname="$output"/"$appdir"_"$version".mpk
	    echo "Creating $mpkname"
	    zip -r0 "$mpkname" .
	    cp res/mipmap-mdpi/icon_64x64.png "$mpkname"_icon_64x64.png
	    popd
	done
done
