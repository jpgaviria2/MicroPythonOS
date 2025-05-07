rm -rf appstore_backend/bundled_apps
mkdir -p appstore_backend/bundled_apps
ls -1 internal_filesystem/apps | while read appdir; do
    echo "Bundling $appdir"
    pushd internal_filesystem/apps/"$appdir"
    version=$( grep "^Version:" META-INF/MANIFEST.MF | cut -d " " -f 2)
    mpkname="../../../appstore_backend/bundled_apps/"$appdir"_"$version".mpk"
    echo "Creating $mpkname"
    zip -r0 "$mpkname" .
    cp res/mipmap-mdpi/icon_64x64.png "$mpkname"_icon_64x64.png 
    popd    
done
