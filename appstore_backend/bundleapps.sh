ls -1 internal_filesystem/apps | while read appdir; do
    echo "$appdir"
    pushd internal_filesystem/apps/"$appdir"
    zip -r0 ../../../bundled_apps/"$appdir"_0.0.1.zip .
    popd    
done
