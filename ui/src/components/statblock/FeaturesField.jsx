
import { Stack, Button, Paper, TextField, Box, Grid } from "@mui/material"
import { Add, Delete } from '@mui/icons-material';

import { reparse_feature } from '../../libs/api.js';
import * as fmt from '../../libs/creature_format.js'
import {  TIME_MEASURES } from '../../constants.js';

import { StyledTextField,  StyledTextAndOptField } from '../FormFields.jsx';
import PoppableField from "./PoppableField.jsx";
import { EditEffect } from "./EditEffect.jsx";
import TitleField from "./TitleField.jsx";
import SpellcastingField from "./SpellcastingFIeld.jsx";
import EditBlock from "./EditBlock.jsx";
import { useEffect, useState } from "react";
import { LongText, OptionalEffects, Recharge, Title, Uses } from "./ComplexParts.js";

function FeatureEditBlock( {feature, setFeature, deleteFeature} ) {

    const setFeaturePart = (part) => (newPart) => {
        const newFeature = {...feature}
        newFeature[part] = newPart
        setFeature(newFeature)
    }

    return (<>
        <Title title={feature.title} setTitle={setFeaturePart("title")} />
        <LongText text={feature.text} setText={setFeaturePart("text")} />
        <Uses uses={feature.uses} setUses={setFeaturePart("uses")} />
        <Recharge recharge={feature.recharge} setRecharge={setFeaturePart("recharge")} />
        <OptionalEffects 
            effects={feature.effects} 
            setEffects = {setFeaturePart("effects")} 
        />
    </>
    )
}


export default function FeaturesField( {statblock, setStatblock, editable, resetFunc}) {

    // useEffect(() => {
    //     if (!statblock.deleted_features) {
    //         setStatblock(s => {
    //             return {...s, deleted_features:{}}
    //         })
    //     }
    // },[statblock])

    const setFeature = (i) => (feature) => {
        const newF = [...statblock.features]
        newF[i] = feature
        setStatblock({...statblock, features: newF})
    }

    const addFeature = () => {
    let newFs = [];
    if (statblock.features) {
        newFs = [...statblock.features]
    }
    newFs.push({title:"New Feature", text:""})
    return setStatblock({...statblock, features:newFs})
    }

    const deleteFeature = (i) => () => {
    let delF = null
    if (!statblock.deleted_features) {
        delF = []
    } else {
        delF = [...statblock.deleted_features]
    }
    delF[i] = true
    return setStatblock({...statblock, deleted_features:delF})
    }

    const regenerateEffects = (i) => () => {
    const title = fmt.title_with_uses(statblock.features[i])
    reparse_feature(title, statblock.features[i].text, 
    (r => {
        statblock.features[i] = r
        setStatblock({...statblock})
    }))
    }

    const onReset = (i) => () => {
        resetFunc("features")(s => {
            const feats = [...statblock.features]
            feats[i] = s.features[i]
            return feats
        })
    }

    const onResetAll = () => {
        resetFunc("features")((sb) => {
            setStatblock(s => {
                return {...s, deleted_features:{}}}
            )
            return sb.features
        })
    }

    if (statblock && statblock.features) {
        return (<> 
        <TitleField editable={editable} text="Features" onAdd={addFeature} onReset={onResetAll} />
        <Stack spacing={2}>
            { statblock?.features?.map((f,i) => {
                if (statblock.deleted_features && statblock.deleted_features[i] === true) {
                    return
                }
                return (
                <PoppableField editable={editable} 
                    text={fmt.format_feature(f)} 
                    key={`feature-popper-${i}`}
                    onGenerate={regenerateEffects(i)}
                    onReset={onReset(i)}
                >
                    <EditBlock title="Feature" onDelete={deleteFeature(i)}>
                        <FeatureEditBlock feature={f} setFeature={setFeature(i)}/>
                    </EditBlock>
                </PoppableField>
            )})
            }
        <SpellcastingField statblock={statblock} setStatblock={setStatblock} editable={editable} resetFunc={resetFunc}/>
        </Stack>
        </> )
    }
}