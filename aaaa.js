const data = '{"Version":"XXX","Statements":[{"aa":"some"},{"b":"ano:,{ther}"},{"bb":3}],"some":0}';
var a=`sadfas${12132}\n`
var r = /123232,asdfdsasdf/
class Perple{

}
// 13123123

var a = new Perple()
const getValuesPositionInArray = arrayKey => data => {
  const arrayNameSeparator = `"${arrayKey}":`;
  const targetArrayIndexOf = data.indexOf(arrayNameSeparator) + arrayNameSeparator.length;
  const arrayStringWithRest = data.slice(targetArrayIndexOf, data.length);
  const charsAfterValue = ['}', ','];
  const charsBeforeKey = ['{', ','];

  const { result } = arrayStringWithRest.split('').reduce(
    (acc, char, idx, array) => {
      if (acc.finished) return acc;
      if (!acc.processingKey && !acc.processingValue && char === '[') acc.nesting += 1;
      if (!acc.processingKey && !acc.processingValue && char === ']') acc.nesting -= 1;

      const shouldFinish = acc.nesting === 0;
      const charIsDblQuote = char === '"';
      const charBefore = array[idx - 1];
      const charAfter = array[idx + 1];
     
      const keyProcessingStarted = (
        charIsDblQuote &&
        !acc.processingKey &&
        !acc.processingValue &&
        charsBeforeKey.includes(charBefore)
      );

      const keyProcessingFinished = (
        charAfter === ':' &&
        charIsDblQuote && 
        acc.processingKey 
      );

      const valueProcessingStarted = (
        char === ':' &&
        !acc.processingKey &&
        !acc.processingValue
      );

      const valueProcessingFinished = (
        (acc.lastProcessedValueType === String
          ? charIsDblQuote
          : true
        ) &&
        acc.processingValue &&
        charsAfterValue.includes(charAfter)
      );

      acc.position += 1;
      acc.finished = shouldFinish;

      if (acc.processingKey && !charIsDblQuote) acc.processedKey += char;
      if (acc.processingValue && !charIsDblQuote) acc.processedValue += char;
      
      if (keyProcessingStarted) {
        acc.processingKey = true;
      } else if (keyProcessingFinished) {
        acc.processingKey = false;
        acc.result[acc.processedKey] = { position: acc.position };
        acc.lastProcessedKey = acc.processedKey;
        acc.processedKey = '';
      }

      if (valueProcessingStarted) {
        acc.processingValue = true;
        acc.lastProcessedValueType = charAfter === '"' ? String : Number;
      } else if (valueProcessingFinished) {
        acc.processingValue = false;
      	acc.result[acc.lastProcessedKey].value = (
          acc.lastProcessedValueType(acc.processedValue)
        );
        acc.processedValue = '';
        acc.lastProcessedKey = '';
        acc.lastProcessedValueType = (v) => v;
      }

      return acc;
    },
    {
      finished: false,
      processingKey: false,
      processingValue: false,
      processedKey: '',
      processedValue: '',
      lastProcessedKey: '',
      lastProcessedValueType: (v) => v,
      nesting: 0,
      position: targetArrayIndexOf + 1,
      result: {}
    }
  )

  return result;

}

const result = getValuesPositionInArray('Statements')(data);

console.log(result)