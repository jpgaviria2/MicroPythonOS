rm -rf appstore_backend/bundled_apps
mkdir -p appstore_backend/bundled_apps
ls -1 internal_filesystem/apps | while read appdir; do
    echo "Bundling $appdir"
    pushd internal_filesystem/apps/"$appdir"
    # TODO: get and append version from manifest instead of hardcoding:
    mpkname="../../../appstore_backend/bundled_apps/"$appdir"_0.0.1.mpk"
    zip -r0 "$mpkname" .
    cp res/mipmap-mdpi/icon_64x64.png "$mpkname"_icon_64x64.png 
    popd    
done
