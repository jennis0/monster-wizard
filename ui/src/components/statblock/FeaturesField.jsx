import { Stack, Button, Paper, TextField, Box } from "@mui/material"
import { Add, Delete } from '@mui/icons-material';

import { reparse_feature } from '../../libs/api.js';
import * as fmt from '../../libs/creature_format.js'
import {  TIME_MEASURES } from '../../constants.js';

import { StyledTextField,  StyledTextAndOptField } from './FormFields.jsx';
import PoppableField from "./PoppableField.jsx";
import { EffectPopper } from "./EffectPopper.jsx";
import TitleField from "./TitleField.jsx";
import SpellcastingField from "./SpellcastingFIeld.jsx";

function FeaturePopper( {feature, setFeature, deleteFeature} ) {

    const setFeatureUses = (field, is_num) => (e) => {
        const newFeature = {...feature}
        if (is_num) {
          newFeature.uses[field] = Number(e.target.value)
        } else {
          newFeature.uses[field] = e.target.value
        }
        setFeature(newFeature)
    }
    
    const addRemoveUses = (e) => {
        const newFeature = {...feature}
        if (!newFeature.uses) {
            newFeature.uses = {slots:0, period:"day"}
        } else {
            delete newFeature.uses
        }
        setFeature(newFeature)
    }

    const setFeatureRecharge = (e) => {
        const newFeature = {...feature}
        newFeature.recharge.from = Number(e.target.value)
        setFeature(newFeature)
    }

    const addRemoveRecharge = (e) => {
        const newFeature = {...feature}
        if (!newFeature.recharge) {
            newFeature.recharge = {from:6, to:6}
        } else {
            delete newFeature.recharge
        }
        setFeature(newFeature)
    }

    const onChange = (field) => (e) => {
        const newFeature = {...feature}
        newFeature[field] = e.target.value
        setFeature(newFeature)
    }

      
    const setFeatureEffect = (j) => (effect) => {
        const newFeature = {...feature}
        newFeature.effects[j] = effect
        setFeature(newFeature)

    }

    const removeFeatureEffect = (j) => () => {
        const newFeature = {...feature}
        newFeature.effects.splice(j, 1)
        setFeature(newFeature)

    }

    const addFeatureEffect = () => {
        const newFeature = {...feature}
        if (!newFeature.effects) {
            newFeature.effects = []
        }
        newFeature.effects.push({})
        setFeature(newFeature)
    }


    return (<>
        <StyledTextField 
            id="feature-title-text"
            placeholder="Feature Title"
            label="Title" 
            value={feature.title} 
            onChange={onChange("title")} 
            key={`feature-titlebox`}
            endButton={<Delete />}
            onEndButtonClick={deleteFeature}
            width="100%"
        />
        <Paper variant="outlined" sx={{p:1, mt:0.5, mb:0.5}} square>
            <TextField 
                value={feature.text} 
                placeholder="Feature Text"
                multiline
                maxRows={100}
                variant="standard"
                InputProps={{disableUnderline:true}}
                sx={{width:"100%"}}
                onChange={onChange("text")}
                key={`feature-textbox`}
            />
        </Paper>
        <StyledTextAndOptField 
            label="Uses"
            textValue={feature.uses ? feature.uses.slots : 0}
            number
            checkbox
            checked = {feature.uses !== undefined}
            onCheckChange={addRemoveUses}
            onTextChange={setFeatureUses("slots")}
            onSelectChange={setFeatureUses("period")}
            midText="per"
            selectValue={feature.uses ? feature.uses.period.replaceAll("_"," "): "-"}
            options={TIME_MEASURES.map(s =>  s.replaceAll("_"," "))}
            width="100%"
            key={`feature-uses`}
            />
        <StyledTextField 
            label="Recharge"
            value={feature.recharge ? feature.recharge.from : 6}
            number
            checkbox
            checked = {feature.recharge !== undefined}
            onCheckChange={addRemoveRecharge}
            onTextChange={setFeatureRecharge}
            width="100%"
            key={`feature-recharge`}
            />
        
        <Button onClick={addFeatureEffect} startIcon={<Add />} sx={{ borderRadius:0,width:"100%"}}>Add Effect</Button>
        {feature.effects ? feature.effects.map((e,j) =>
                <EffectPopper 
                    effect={e} 
                    setEffect={setFeatureEffect(j)} 
                    removeEffect={removeFeatureEffect(j)} 
                    key={`feature-effects-field-${j}`}
                />
                ) : <></>
        }
        </>
    )
}


export default function FeaturesField( {statblock, setStatblock, editable}) {

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
    let newFs = statblock.features
    newFs.splice(i, 1)
    return setStatblock({...statblock, features:newFs})
  }

  const regenerateEffects = (i) => () => {
    console.log(i, statblock.features[i])
    const title = fmt.title_with_uses(statblock.features[i])
    reparse_feature(title, statblock.features[i].text, 
    (r => {
      statblock.features[i] = r.result
      setStatblock({...statblock})
    }))
  }

  console.log(statblock.features)

  if (statblock && statblock.features) {
    return (<> 
    <TitleField editable={editable} text="Features" onAdd={addFeature} />
    <Stack spacing={2}>
        { statblock?.features?.map((f,i) => 
            (
                <PoppableField editable={editable} 
                text={fmt.format_feature(f)} 
                key={`feature-popper-${i}`}
                onGenerate={regenerateEffects(i)}
            >
              <Box key={`feature-set-value-${i}`} square variant="outlined" 
              sx={{padding:0, m:0, flexDirection:"column", display:"flex", mb:1.5, width:500}}>
                <FeaturePopper feature={f} setFeature={setFeature(i)} deleteFeature={deleteFeature(i)}/>
              </Box>
          </PoppableField>))
        }
    <SpellcastingField statblock={statblock} setStatblock={setStatblock} editable={editable} />
    </Stack>
      </> )
  }
}