/**
 * 
 * Sample UIPath Bot Generator for IBM Process Mining.
 * 
 * Updated : 06 March 2023
 * Version  : 1.3
 * 
 * This sample generator can be used to build UIPath Bot for IBM Process Mining.
 * Refer documentation for more details: https://ibm.biz/cust-rpa-vendor
 */


/*
* This is the main function used by the Script Execution Engine. 
* The name of the function and the number of parameters should not be altered.
* The Script Execution Engine identifies the function by name, and injects the data required
* by the script to generate the bot into the function parameters.
* The parameter names can be changed, but make sure to change all the references in the code.
* Please refer the Custom RPA Bot Generation documentation [https://ibm.biz/cust-rpa-vendor] 
* for more details on the structure and usage of each of the parameters.
*
* This script supports generation of multiple Bots in single execution.
* To do this, create a new function similar to the function "build_xaml" and append the result of it's
* execution as a new entry in the "result" object.
* The script engine treats each entry in the response "result" object as a separate file.
*/
function generateBot(dataModel, snippets, contextualData) {

     const content_xaml = build_xaml(dataModel, snippets, contextualData);

     const xaml_file = {
         "name":"uipath",
         "extension":".xaml",
         "value":content_xaml
     };

     // Any number of files can be appended to the output object.
     const result = {
         "files": [xaml_file]
     }
     return result;
 }

 var processedNodes = [];
 var referenceNames = [];

 /**
  * Function that deals with generation of the UIPath Bot.
  */
 function build_xaml(dataModel, snippets, contextualData) {
     var uiPathBot = [];
          uiPathBot.push(snippets.preExecutionSnippet + "\n");

          // Initialize the State Machine
          uiPathBot.push('<StateMachine InitialState="{x:Reference '+ formatReferenceId(dataModel.startNodes[0]) + '}" sap2010:WorkflowViewState.IdRef="StateMachine_UIPath">' + "\n");
          processNode(dataModel, snippets, dataModel.startNodes[0], uiPathBot, contextualData);
          // State Machine Variables - Mark each variable from contextual Data as a StateMachine variable
          uiPathBot.push('<StateMachine.Variables>' + "\n");
          contextualData.forEach((a) => {
              uiPathBot.push('<Variable x:TypeArguments="' + mapToVBDataType(a) + '" Name="'+ a.rpaVariableName + '" />' + "\n");
          });
          uiPathBot.push('</StateMachine.Variables>' + "\n");
          uiPathBot.push('</StateMachine>' + "\n");
          uiPathBot.push(snippets.postExecutionSnippet + "\n");
          return uiPathBot.join('');
 }

/**
 * This function is invoked iteratively until all the nodes in the BPMN object are processed.
 */
 function processNode(model, snippets, element, uiPathBot, contextualData) {
             if (!element || processedNodes.filter(item => item == element).length > 0)
                 return;
             // Add element to the processedNodes array, so that we don't need to process it again
             processedNodes.push(element);

             // process the element
             if(model.endNodes.indexOf(element) > -1) {
                 uiPathBot.push('<State x:Name="' + formatReferenceId(element) + '" DisplayName="' + element + '" sap2010:WorkflowViewState.IdRef="' + formatReferenceId(element) + '" IsFinal="True" >' + "\n");
             } else {
                 uiPathBot.push('<State x:Name="' + formatReferenceId(element) + '" DisplayName="' + element + '" sap2010:WorkflowViewState.IdRef="' + formatReferenceId(element) + '">' + "\n");
             }
             uiPathBot.push('<State.Entry>' + "\n");
             var snippet = null;
             var filteredArray = snippets.tasks.filter(item => item.taskName == element);
             if(filteredArray && filteredArray.length > 0) {
                 snippet = filteredArray[0].snippets[0].snippet;
             }
             if(!snippet) {
                 // Human Mandatory Tasks will not have associated Snippets in Task Mining.
                 if(isHumanMandatoryTask(model.humanMandatoryInfo, element)) {
                    snippet =  `<!-- '${element}' must be performed by a human and it cannot be automated. -->`;
                 } else {
                    snippet =  `<!-- No RPA snippet found for task : ${element} -->`;
                    //throw new Error (`No RPA snippet found for task : ${element} `);
                 }
             }
             uiPathBot.push(snippet + "\n");
             uiPathBot.push('</State.Entry>' + "\n");
             // if the processed element is in the end-nodes, return
             if(model.endNodes.indexOf(element) > -1) {
                 uiPathBot.push('</State>' + "\n");
                 return;
             }
             uiPathBot.push('<State.Transitions>' + "\n");
             // Find a direct destination element and process it
             var sourceNode = model.transitions.filter(item => item.source == element)[0];
             var destination;
             if(sourceNode.destination) {
                 // This is a direct transition, build the Direct UI Path Transition
                 destination = sourceNode.destination;
                 uiPathBot.push('<Transition DisplayName="'+ element + '-TO-' + destination + '" sap2010:WorkflowViewState.IdRef="' + formatReferenceId(element) + '_' + formatReferenceId(destination) + '" To="{x:Reference '+ formatReferenceId(destination) + '}">' + "\n");
                 uiPathBot.push('</Transition>' + "\n");
                 uiPathBot.push('</State.Transitions>' + "\n");
                 uiPathBot.push('</State>' + "\n");
                 processNode(model, snippets, destination, uiPathBot, contextualData);
             } else {
             // This must be a rule based transition. Build the conditional transition logic here
                 Object.keys(sourceNode.rules).forEach((element) => {
                   uiPathBot.push('<Transition DisplayName="'+ sourceNode.source + '-TO-' + element + '" sap2010:WorkflowViewState.IdRef="' + formatReferenceId(sourceNode.source) + '_' + formatReferenceId(element) + '" To="{x:Reference '+ formatReferenceId(element) + '}">' + "\n");
                   uiPathBot.push('<Transition.Condition>' + buildTransitionExpression(sourceNode.rules[element], contextualData) +'</Transition.Condition>' + "\n");
                   uiPathBot.push('</Transition>' + "\n");
                 });
                 uiPathBot.push('</State.Transitions>' + "\n");
                 uiPathBot.push('</State>' + "\n");
                 // Now, process each destination node
                 Object.keys(sourceNode.rules).forEach((element) => {
                     processNode(model, snippets, element, uiPathBot, contextualData);
                 });
             }
         }


         /**
          * All special characters in the element  are replaced with 0s to form the referenceIds.
          * While doing this, it is possible that two or more elements end up hacing the same name,
          * which may lead to wrong execution .
          * To prevent this, the function is recursively invoked until a unique reference name is 
          * generated.
          */
         function formatReferenceId(element) {

             // If there is already a mapping available for this element, use it
             if(referenceNames.filter(a => a.element === element).length > 0) {
                 return referenceNames.filter(a => a.element === element)[0].reference;
             } else if(referenceNames.filter(a => a.element === element).length == 0){
                 // Replace special Characters from Reference Ids with 0s
                 var refName =  "__".concat(element.replace(/[^a-zA-Z0-9]/g, "0"));
                 if(referenceNames.filter(a => a.reference === refName).length == 0) {
                     // Add an entry to the references Array and return
                     referenceNames.push({"element": element, "reference": refName});
                     return refName;
                 } else {
                 // Keep adding 0s until a unique name is found
                 refName = refName.concat("0");
                 while (referenceNames.filter(a => a.reference === refName).length > 0) {
                       refName = refName.concat("0");
                 }
                 referenceNames.push({"element": element, "reference": refName});
                 return refName;
             }
         }
     }


    /**
    * Builds and returns a Visual Basic rule expression for the given BPMN Rule
    */
   function buildTransitionExpression(ruleJson, contextualData) {
           var transition = '[';
           if( ruleJson['OR']) {
               ruleJson['OR'].forEach(function(orExp, idx1, orArray){
                   transition += "(";
                   if(orExp['AND']) {
                       orExp['AND'].forEach((andExp, idx2, andArray) => {
                           transition += buildUIPathVBExpression(andExp, contextualData);
                           if(idx2 !== andArray.length - 1) {
                               transition += ' And '
                           }
                       })
                   }
                   transition += ')'
                   if(idx1 !== orArray.length - 1) {
                       transition += ' Or '
                   }
               })
           }
           transition+= "]";
           return transition;
       }

        /**
         * Build the Visual Basic expressins for the different operators in the BPMN Rule Expressions.
         */
       function buildUIPathVBExpression(exp, contextualData) {
             // If exp is null, return
             if(!exp) return "";
             switch(exp.operator) {
                case "IS":
                    return getAttributeType(exp.attribute, contextualData) == "date" ? buildDateTimeVBExpression(exp, exp.operator) : buildEqualityExpValue(exp.value, exp.attribute);
                case "IS NOT":
                    return getAttributeType(exp.attribute, contextualData) == "date" ? buildDateTimeVBExpression(exp, exp.operator) : "Not (" +  buildEqualityExpValue(exp.value, exp.attribute) + ")";
                case "<":
                    return getAttributeType(exp.attribute, contextualData) == "date" ? buildDateTimeVBExpression(exp, exp.operator) : exp.attribute + " &lt; " + exp.value;
                case ">":
                     return getAttributeType(exp.attribute, contextualData) == "date" ? buildDateTimeVBExpression(exp, exp.operator) : exp.attribute + " &gt; " + exp.value;
                case "<=":
                    return getAttributeType(exp.attribute, contextualData) == "date" ? buildDateTimeVBExpression(exp, exp.operator) : exp.attribute + " &lt;= " + exp.value;
                case ">=":
                    return getAttributeType(exp.attribute, contextualData) == "date" ? buildDateTimeVBExpression(exp, exp.operator) : exp.attribute + " &gt;= " + exp.value;
                case "IN":
                     return buildUIPathVBExpressionForIN(exp, contextualData);
                case "NOT IN":
                     return buildUIPathVBExpressionForNotIN(exp, contextualData);
                case "INSIDE":
                     return buildUIPathVBExpressionForInside(exp);
            }
       }

        /**
         * Build the Visual Basic expressins for the DateTime attributes in BPMN Rule expressions.
         */
       function buildDateTimeVBExpression(exp, operator) {

             switch(operator) {
                 case "IS":
                     return "DateTime.Compare(" + exp.attribute + ", " + buildUIPathDateTimeObjectFromEpochTimeStamp(exp.value) + ") = 0";
                 case "IS NOT":
                     return "Not(DateTime.Compare(" + exp.attribute + ", " + buildUIPathDateTimeObjectFromEpochTimeStamp(exp.value) + ") = 0)";
                 case "<":
                    return "DateTime.Compare(" + exp.attribute + ", " + buildUIPathDateTimeObjectFromEpochTimeStamp(exp.value) + ") &lt; 0";
                 case ">":
                     return "DateTime.Compare(" + exp.attribute + ", " + buildUIPathDateTimeObjectFromEpochTimeStamp(exp.value) + ") &gt; 0";
                 case "<=":
                    return "DateTime.Compare(" + exp.attribute + ", " + buildUIPathDateTimeObjectFromEpochTimeStamp(exp.value) + ") &lt;= 0";
                 case ">=":
                    return "DateTime.Compare(" + exp.attribute + ", " + buildUIPathDateTimeObjectFromEpochTimeStamp(exp.value) + ") &gt;= 0";

             }
       }

     /**
      * Returns the type of an attribute. 
      * Default is "string".
      */ 
     function getAttributeType(attrName, contextualData) {
             if(contextualData && contextualData.filter(a => a.rpaVariableName == attrName).length > 0) {
                 return contextualData.filter(a => a.rpaVariableName == attrName)[0].rpaVariableType;
             }
             return "string";

       }


       /**
        * Maps a contextual Data variable type to VB Data Type
        */ 
       function mapToVBDataType(attribute) {
         switch(attribute.rpaVariableType) {
                case "string":
                    return "x:String";
                case "numeric":
                    return "x:Decimal";
                case "integer":
                    return "x:Int32";
                case "long":
                    return "x:Int32";
                case "double":
                    return "x:Decimal";
                case "date":
                    return "s:DateTime";
                 default:
                    return "x:String";
         }
       }

       /**
        * Build the UIPath VB expression for IN Operator
        */ 
       function buildUIPathVBExpressionForIN(exp, contextualData) {
            if(exp.value.startsWith('[') && exp.value.endsWith(']')) {
                return normalizeExpValue(exp.value, exp.attribute, contextualData);
            } else {
                return exp.value +".Contains(" + exp.attribute +")";
            }
      }

      /**
        * Build the UIPath VB expression for NOT IN Operator
        */
      function buildUIPathVBExpressionForNotIN(exp, contextualData) {
           if(exp.value.startsWith('[') && exp.value.endsWith(']')) {
                  return "Not(" + normalizeExpValue(exp.value, exp.attribute, contextualData) + ")";
          } else {
              return "Not(" + exp.value +".Contains(" + exp.attribute +"))";
          }
      }

      /**
        * Build the UIPath VB expression for INSIDE Operator
        */
      function buildUIPathVBExpressionForInside(exp) {
            var expression = "";
            var strVarArray = exp.value.replace('[', '').replace(']','').replace('(','').replace(')','').split(',');
            if(exp.value.startsWith('(')) {
                 expression = exp.attribute + " &gt; " + strVarArray[0] + " And ";
            } else if(exp.value.startsWith('[')) {
                 expression = "(" + exp.attribute + " &gt; " + strVarArray[0] + " Or " + exp.attribute + " = " + strVarArray[0] + ") And "
            }
            if(exp.value.endsWith(')')) {
                 expression = expression + exp.attribute + " &lt; " + strVarArray[1];
            } else if(exp.value.endsWith(']')) {
                 expression = expression + "(" + exp.attribute + " &lt; " + strVarArray[1] + " Or " + exp.attribute + " = " + strVarArray[1] + ")"
            }
            return expression;
      }

       /**
        * Build the UIPath VB expression for IS operator
        */
      function buildEqualityExpValue(val, attribute) {

             if(val == 'Missing') {
                 return  attribute + " Is Nothing";
             } else {
                 return attribute + " = " + val;
             }
      }

        /**
         * Processes a rule expression until the equivalent Visual Basic expression is formed.
         * For expressions  are of IN / NOT IN / INSIDE operations, the processExpValNormalization
         * function is invoked iteratively until all the values inside these expressions are processed.
         */ 
        function normalizeExpValue(val, attribute, contextualData) {
            var strRtnArray = [];
            processExpValNormalization(strRtnArray, val.trim(), attribute, contextualData);

            if(strRtnArray.length > 0) {
              if(strRtnArray.indexOf('Is Nothing') >= 0) {
                 // This is an IN / NOT IN / INSIDE statement containing a "Missing". This needs to be handled differently
                 var pos = strRtnArray.indexOf('Is Nothing');
                 // Splice the array to remove this item
                 strRtnArray.splice(pos, 1);
                 return "{" + strRtnArray.join(',') + "}" + ".Contains(" + attribute + ") Or " +  attribute + " Is Nothing";

              } else {
                 return "{" + strRtnArray.join(',') + "}" + ".Contains(" + attribute + ")";
             }
            }
         }


        function processExpValNormalization(strRtnArray, val, attribute, contextualData) {
        var valStr = val.replace('[', '').replace(']','');
        var strVarArray = valStr.split(',');
              if(strVarArray.length > 1) 
              {
                    // Value is a comma separated list from an IN, NOT IN or INSIDE operator
                    strVarArray.forEach((a) => {
                     processExpValNormalization(strRtnArray, a.trim(), attribute, contextualData);
                      });
              }
                else if(valStr.trim() == "Missing") {
                    strRtnArray.push("Is Nothing");
                }
                else {
                  strRtnArray.push(valStr);
                }
        }

        /**
         * IBM Process Mining treats DateTime objects as epoch timestamps.
         * The rule expressins will have attribute values in this format.
         * This function converts an epoch timestamp to a Visual Basic Date Time object.
         */
        function buildUIPathDateTimeObjectFromEpochTimeStamp(epochTimeStamp) {
             var date = new Date(Number(epochTimeStamp));
             var year = date.getFullYear();
             var month = padZeroesIfNeeded(date.getMonth() + 1);
             var day = padZeroesIfNeeded(date.getDate());
             var hours = padZeroesIfNeeded(date.getHours());
             var minutes = padZeroesIfNeeded(date.getMinutes());
             var seconds = padZeroesIfNeeded(date.getSeconds());
             return "new DateTime(" + year + "," + month + "," + day + "," + hours + "," + minutes + "," + seconds + ")";
        }
         function padZeroesIfNeeded(val) {
             return (val < 10) ? "0"+val : String(val);
         }

        /**
        * Returns true if the task being processed is Human Mandatory.
        * Such tasks will not have a snippet in the generated Not. Insted we just add a comment
        * indicating the requirement of a human action.
        */
        function isHumanMandatoryTask(humanMandatoryInfo, element) {
            if(!humanMandatoryInfo || humanMandatoryInfo.length == 0){
                return false;
            }
            if(humanMandatoryInfo.filter(t => t.taskName == element && t.humanMandatory == true).length > 0) {
                return true;
            }
            return false;
        }