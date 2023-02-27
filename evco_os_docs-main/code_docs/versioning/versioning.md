# git merge: commit and tags

## using git tags to create release (version) and merge
___
source: https://stackoverflow.com/a/18223354/18024965

to create tag on current branch: (only creates locally)
using as example:
- `feature` (to be merged)
- `develop` (branch to merge into) as example

```console
evco_os$ git checkout feature # if you are not in feature
evco_os$ git tag <tagname>
```

to push your tags to remote repository:
```console
evco_os$ git push origin --tags
```

or for just one tag:
```console
evco_os$ git push origin <tagname>
```

## decide on the commmit tag you want to merge
___
In this case, merging a commit from `feature` onto `develop` 

while in feature branch (git checkout feature)
```console
evco_os$ git checkout develop
evco_os$ git merge <commit-hash or tagname>
```

example:
```console
evco_os$ git checkout develop
evco_os$ git merge 1.0.3.demo
evco_os$ # OR 
evco_os$ git merge b233baa7da9665a8441b0be5990651670db34af9
```




# done!