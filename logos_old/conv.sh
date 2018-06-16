#!/bin/bash


for i in *.png; do sips -s format jpeg -s formatOptions best $i --out converted/$i.jpg;done
