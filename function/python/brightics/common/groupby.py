# -*- coding: utf-8 -*-
from brightics.common.repr import BrtcReprBuilder

import pandas as pd
import numpy as np
import time

GROUP_KEY_SEP = '\u0002'


def time_usage(func):

    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        print("{} elapsed time: {} s".format(func, end - start))
        return res

    return wrapper


def _grouped_data(group_by, group_key_dict):
    grouped_data = {
        'data': dict(),
        'group_by': group_by,
        'group_key_dict': group_key_dict
    }
    return grouped_data


@time_usage
def _sample_result(function, table, model, params, group_key_dict):
    sample_group = [*group_key_dict][0]
    sample_result = _run_function(function, table, model, params, sample_group)

    return sample_result


@time_usage
def _function_by_group_key(function, table, model, params, res_dict, group_key_dict, res_keys):
    for group_key in group_key_dict:
        res_group = _run_function(function, table, model, params, group_key)
        
        for res_key in res_keys:
            res_dict[res_key]['_grouped_data']['data'][group_key] = res_group[res_key]
        
    return res_dict


def _run_function(function, table, model, params, group):
    if table is not None and model is None:
        res_group = function(table=table['_grouped_data']['data'][group], **params)
    elif table is not None and model is not None:
        res_group = function(table=table['_grouped_data']['data'][group],
                                    model=model['_grouped_data']['data'][group], **params)
    else:
        res_group = function(model=model['_grouped_data']['data'][group], **params)
    
    return res_group

        
@time_usage
def _function_by_group(function, table=None, model=None, group_by=None, **params):
    if table is None and model is None:
        raise Exception('This function requires at least one of a table or a model')
     
    if isinstance(table, pd.DataFrame) and model is None and group_by is None:
        raise Exception('This function requires group_by.')
     
    if isinstance(model, dict) and '_grouped_data' not in model:
        raise Exception('Unsupported model. model requires _grouped_data.')
    
    if isinstance(model, dict):
        group_key_dict = model['_grouped_data']['group_key_dict']
        group_by = model['_grouped_data']['group_by']
    
    if isinstance(table, pd.DataFrame):
        table, group_key_dict = _group(table, group_by)  # use group keys from table even there is a model.
    
    print('Number of groups: {}'.format(len(group_key_dict)))
    
    sample_result = _sample_result(function, table, model, params, group_key_dict)
        
    res_keys = [*sample_result]
    df_keys = [k for k, v in sample_result.items() if isinstance(v, pd.DataFrame)]
    model_keys_containing_repr = [k for k, v in sample_result.items() if isinstance(v, dict) and '_repr_brtc_' in v]
    
    res_dict = dict()
    for res_key in res_keys:
        res_dict[res_key] = {'_grouped_data': _grouped_data(group_by, group_key_dict)}
        
    res_dict = _function_by_group_key(function, table, model, params, res_dict, group_key_dict, res_keys)
    
    for repr_key in model_keys_containing_repr:
        rb = BrtcReprBuilder()
        from brightics.common.json import to_json
        print(to_json(res_dict[repr_key]['_grouped_data']))
        for group in group_key_dict:
            print(group)
            print(type(group))
            rb.addMD('{group}'.format(group=group))
            rb.merge(res_dict[repr_key]['_grouped_data']['data'][group]['_repr_brtc_'])
        res_dict[repr_key]['_repr_brtc_'] = rb.get()    
            
    for df_key in df_keys:
        res_dict[df_key] = _flatten(res_dict[df_key])
    
    return res_dict


def _group_key_from_list(list_):
    return GROUP_KEY_SEP.join([str(item) for item in list_])


def _group_key_dict(group_keys, groups):  # todo
    group_key_dict = dict()
    for key, group in zip(group_keys, groups):
        if key not in group_key_dict:
            group_key_dict[key] = group.tolist()
    
    return group_key_dict

    
@time_usage
def _group(table, group_by):
    start = time.time()
    
    groups = table[group_by].values
    print(type(groups))
    print(groups.shape)
    print(1, time.time() - start)
    group_keys = np.apply_along_axis(_group_key_from_list, axis=1, arr=groups)
    # group_keys = np.vectorize(_group_key_from_list)(groups)
    # group_keys = [GROUP_KEY_SEP.join([str(item) for item in _]) for _ in groups]
    print(2, time.time() - start)
    group_key_dict = _group_key_dict(group_keys, groups)
    print(3, time.time() - start)
    
    res_dict = {'_grouped_data': _grouped_data(group_by=group_by, group_key_dict=group_key_dict)}  # todo dict?
    for group_key in group_key_dict:
        data = table[group_keys == group_key]
        data.reset_index(drop=True)
        res_dict['_grouped_data']['data'][group_key] = data
    print(4, time.time() - start)
    return res_dict, group_key_dict


@time_usage
def _add_group_cols_front_if_required(table, keys, group_cols, group_key_dict):
    reverse_keys = group_key_dict[keys]  # todo
    print(type(reverse_keys))
    reverse_keys.reverse()
    columns = table.columns
    reverse_group_cols = group_cols.copy()
    reverse_group_cols.reverse()
    
    for group_col, key in zip(reverse_group_cols, reverse_keys):
        if group_col not in columns:
            table.insert(0, group_col, key)

    return table


@time_usage
def _flatten(grouped_table):
    group_cols = grouped_table['_grouped_data']['group_by']
    group_key_dict = grouped_table['_grouped_data']['group_key_dict']
    return pd.concat([_add_group_cols_front_if_required(v, k, group_cols, group_key_dict) 
                      for k, v in grouped_table['_grouped_data']['data'].items() if v is not None],
                      ignore_index=True, sort=False)
