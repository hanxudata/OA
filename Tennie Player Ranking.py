import pandas as pd
import numpy as np

def match_count(match):
    if data_match.loc[match,'winnerset2']+ data_match.loc[match,'winnerset2']==0:
        match_counts=1
    elif data_match.loc[match,'winnerset3']+ data_match.loc[match,'winnerset3']==0:
        match_counts=2
    elif data_match.loc[match,'winnerset4']+ data_match.loc[match,'winnerset4']==0:
        match_counts=3
    elif data_match.loc[match,'winnerset5']+ data_match.loc[match,'winnerset5']==0:
        match_counts=4
    else:
        match_counts=5
    return match_counts

def coeff(x):
    return 1/(np.log(np.abs(x)+1)+1)

def player_socre_change(player_score,winner_player,loser_player,score):
    player_score.loc[player_score['player']==winner_player,
                             'score']=np.round(player_score.loc[player_score['player']==winner_player,'score']+score,2)
    player_score.loc[player_score['player']==loser_player,
                             'score']=np.round(player_score.loc[player_score['player']==loser_player,'score']-score,2)

def match_player_rank(data_match):
    player_score=pd.DataFrame({'player':player,'score':5}).reset_index(drop=True)
    for match in range(len(data_match)):
        winner_player=data_match.loc[match,'winner1id']
        loser_player=data_match.loc[match,'loser1id']
        if winner_player==0:
            winner_score=5
        else:
            winner_score=player_score.loc[player_score['player']==winner_player,'score'].tolist()[0]
        if loser_player==0:
            loser_score=5
        else:
            loser_score=player_score.loc[player_score['player']==loser_player,'score'].tolist()[0]

    #     print("mathch:{},winner_score:{},loser_score:{}".format(match,winner_score,loser_score))
        match_counts=match_count(match)
        match_scores=data_match.iloc[match,2:12].diff(-5).sum()
        score_avg=np.round(match_scores/match_counts,2)

    #     print("mathch:{},match_counts:{},match_scores:{},score_avg:{}".format(match,match_counts,match_scores,score_avg))

        if  winner_score==loser_score:

            if score_avg>=1:
                player_socre_change(player_score,winner_player,loser_player,score_avg)
            else:
                player_socre_change(player_score,winner_player,loser_player,1)
        else:
            score_change=score_avg-(winner_score-loser_score)*coeff(winner_score-loser_score)
            player_socre_change(player_score,winner_player,loser_player,score_change)

        data_match.loc[match,'loser_score']=loser_score
        data_match.loc[match,'winner_score']=winner_score
        data_match.loc[match,'score_avg']=score_avg

    return player_score,data_match


if __name__ == '__main__':

    mathch = pd.read_csv('FINALutrdatascienceinternship2019.csv')
    match_column = ['resultid', 'resultdate', 'winnerset1', 'winnerset2', 'winnerset3', 'winnerset4', 'winnerset5',
                    'loserset1',
                    'loserset2', 'loserset3', 'loserset4', 'loserset5']
    mathch_melt = pd.melt(mathch, id_vars=match_column, value_vars=['winner1id', 'loser1id'], var_name='type',
                          value_name='palyer_id')
    mathch_melt = mathch_melt.sort_values(['palyer_id', 'resultdate'], ascending=False).reset_index(drop=True)
    mathch_melt = mathch_melt.groupby(['palyer_id']).head(30)

    player = mathch_melt['palyer_id'].drop_duplicates()

    mathch_pivot = pd.pivot_table(mathch_melt, index=match_column, columns='type', fill_value=0).reset_index()
    match_column.extend(['loser1id', 'winner1id'])
    mathch_pivot.columns = match_column
    mathch_pivot[['loser1id', 'winner1id']] = mathch_pivot[['loser1id', 'winner1id']].astype("int64")

    data_match = mathch_pivot.copy()
    data_match = data_match.sort_values('resultid')

    player_score, data_match=match_player_rank(data_match)
    player_score=player_score.sort_values('score',ascending=False).reset_index(drop=True)
    player_score['rank']=player_score.index+1
    player_score[['rank','playerid']].to_csv('playe_rank.csv',index=False)
    data_match.to_csv('data_match.csv',index=False)
