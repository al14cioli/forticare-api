#! /bin/bash



usage() { 
    echo "$0 -f <REGISTRATIONCODE.csv> -d"
    exit 0
}

[ $# -eq 0 ] && usage

while getopts "hf:" arg
do
    case $arg in
        f)
            file=${OPTARG}
            ;;
    esac
done

cat ${file} | while read line
do
    # continue if line is a comment
    { grep -qe '^#' <<< ${line} ;} && continue
    
    regcode=`echo ${line} | cut -d ',' -f1`
    ipaddr=`echo ${line} | cut -d ',' -f2`
    desc=`echo ${line} | cut -d ',' -f3`
    sn=`echo ${line} | cut -d ',' -f4`
    
    echo "*** Registration code [${regcode}], IP address [${ipaddr}], description=[${desc}], SN [${sn}]"
    ./ftnt-register-asset.py --code "${regcode}" --description "${desc}" --address "${ipaddr}" --serial "${sn}" --lic --verbose
done
